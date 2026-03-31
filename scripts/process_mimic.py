#!/usr/bin/env python3
"""
Process MIMIC-IV Demo lab data into Spanish blood test training samples.
Maps MIMIC lab test names to Spanish marker names and generates
JSONL in the same format as synthetic_blood_es.jsonl.
"""

import json
import os
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

SEED = 123
random.seed(SEED)

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "mimic_blood_es.jsonl")

# ---------------------------------------------------------------------------
# Marker definitions (same as generate_dataset.py)
# ---------------------------------------------------------------------------

@dataclass
class Marker:
    name: str
    unit: str
    low_m: float
    high_m: float
    low_f: Optional[float] = None
    high_f: Optional[float] = None
    decimals: int = 0
    rec_high: str = ""
    rec_low: str = ""
    abs_min: float = 0.0
    abs_max: float = 0.0
    # MIMIC label(s) that map to this marker
    mimic_labels: list = field(default_factory=list)
    # Unit conversion factor from MIMIC units to our units (multiply)
    unit_conversion: float = 1.0


MARKERS = [
    Marker(
        name="Glucosa", unit="mg/dL",
        low_m=70, high_m=100, decimals=0,
        abs_min=50, abs_max=350,
        mimic_labels=["Glucose"],
        rec_high=(
            "Reducir azucares refinados y harinas blancas. Aumentar el consumo de fibra "
            "soluble (legumbres, avena, cebada). Incluir canela y vinagre de manzana en la dieta. "
            "Priorizar carbohidratos de bajo indice glucemico (quinoa, boniato, pan integral). "
            "Caminar al menos 30 minutos al dia, preferiblemente despues de las comidas. "
            "Mantener horarios regulares de comida y no saltarse el desayuno."
        ),
        rec_low=(
            "Asegurar comidas frecuentes y equilibradas cada 3-4 horas. "
            "Incluir carbohidratos complejos en cada comida (arroz integral, pasta integral, patatas). "
            "Combinar siempre con proteina y grasa saludable para estabilizar la glucemia. "
            "Llevar siempre un snack de emergencia (frutos secos, fruta). "
            "Evitar el ayuno prolongado y el ejercicio intenso en ayunas."
        ),
    ),
    Marker(
        name="Colesterol Total", unit="mg/dL",
        low_m=125, high_m=200, decimals=0,
        abs_min=90, abs_max=380,
        mimic_labels=["Cholesterol, Total"],
        rec_high=(
            "Reducir el consumo de grasas saturadas (embutidos, mantequilla, quesos curados). "
            "Aumentar el consumo de fibra soluble (avena, manzanas, legumbres). "
            "Incluir fitoesteroles: nueces, almendras, aceite de oliva virgen extra. "
            "Consumir pescado azul 2-3 veces por semana (salmon, caballa, sardinas). "
            "Realizar ejercicio aerobico moderado al menos 150 minutos semanales."
        ),
        rec_low=(
            "Asegurar un aporte adecuado de grasas saludables: aceite de oliva, aguacate, frutos secos. "
            "Revisar que la dieta no sea excesivamente restrictiva en grasas. "
            "Incluir huevos (la yema contiene colesterol y nutrientes esenciales). "
            "Consultar con el medico para descartar causas subyacentes."
        ),
    ),
    Marker(
        name="LDL", unit="mg/dL",
        low_m=50, high_m=130, decimals=0,
        abs_min=30, abs_max=260,
        mimic_labels=["Cholesterol, LDL, Calculated", "Cholesterol, LDL, Measured"],
        rec_high=(
            "Reducir grasas saturadas y trans (bolleria industrial, frituras, carnes procesadas). "
            "Aumentar omega-3: salmon, sardinas, nueces, semillas de lino y chia. "
            "Consumir 2-3 raciones de legumbres a la semana (lentejas, garbanzos, alubias). "
            "Anadir ajo y cebolla a las comidas por su efecto hipolipemiante. "
            "Sustituir snacks procesados por un punado de almendras o nueces al dia."
        ),
        rec_low=(
            "Niveles bajos de LDL generalmente no requieren intervencion dietetica especifica. "
            "Mantener una dieta equilibrada con grasas saludables. "
            "Consultar con el medico si los niveles son extremadamente bajos."
        ),
    ),
    Marker(
        name="HDL", unit="mg/dL",
        low_m=40, high_m=100, low_f=50, high_f=100, decimals=0,
        abs_min=20, abs_max=120,
        mimic_labels=["Cholesterol, HDL"],
        rec_high=(
            "Niveles elevados de HDL suelen ser protectores. Mantener los habitos actuales. "
            "Continuar con ejercicio regular y consumo de grasas monoinsaturadas."
        ),
        rec_low=(
            "Aumentar la actividad fisica aerobica (correr, nadar, bicicleta) al menos 30 minutos, 5 dias/semana. "
            "Incluir grasas monoinsaturadas: aceite de oliva virgen extra, aguacate, almendras. "
            "Consumir pescado azul 3 veces por semana. Reducir carbohidratos refinados y azucares. "
            "Evitar el tabaco. Moderar el consumo de alcohol. "
            "Anadir semillas de lino molidas a ensaladas o yogur."
        ),
    ),
    Marker(
        name="Trigliceridos", unit="mg/dL",
        low_m=35, high_m=150, decimals=0,
        abs_min=25, abs_max=600,
        mimic_labels=["Triglycerides"],
        rec_high=(
            "Reducir drasticamente azucares simples, refrescos y zumos industriales. "
            "Eliminar el alcohol o reducirlo al minimo. "
            "Aumentar omega-3: salmon, caballa, sardinas, nueces, semillas de chia. "
            "Reducir harinas refinadas y sustituir por cereales integrales. "
            "Limitar la fruta a 2-3 piezas al dia, priorizando frutas de bajo indice glucemico (fresas, arandanos). "
            "Realizar ejercicio aerobico diario de al menos 30 minutos."
        ),
        rec_low=(
            "Niveles bajos de trigliceridos generalmente no son preocupantes. "
            "Asegurar un aporte calorico suficiente si hay perdida de peso involuntaria. "
            "Consultar con el medico si los niveles son extremadamente bajos."
        ),
    ),
    Marker(
        name="Hemoglobina", unit="g/dL",
        low_m=13, high_m=17, low_f=12, high_f=16, decimals=1,
        abs_min=6, abs_max=22,
        mimic_labels=["Hemoglobin"],
        rec_high=(
            "Aumentar la hidratacion: beber al menos 2 litros de agua al dia. "
            "Reducir el consumo de carnes rojas. Evitar suplementos de hierro sin supervision medica. "
            "Consultar con el medico para descartar policitemia u otras causas."
        ),
        rec_low=(
            "Aumentar alimentos ricos en hierro: carnes rojas magras, higado, mejillones, almejas. "
            "Incluir legumbres (lentejas, garbanzos) y verduras de hoja verde (espinacas, acelgas). "
            "Combinar estos alimentos con fuentes de vitamina C (naranja, pimiento, kiwi) para mejorar la absorcion. "
            "Evitar tomar te, cafe o lacteos junto con las comidas principales. "
            "Considerar suplementacion de hierro bajo supervision medica."
        ),
    ),
    Marker(
        name="Hematocrito", unit="%",
        low_m=40, high_m=54, low_f=36, high_f=48, decimals=1,
        abs_min=20, abs_max=65,
        mimic_labels=["Hematocrit"],
        rec_high=(
            "Aumentar significativamente la ingesta de liquidos (agua, infusiones, caldos). "
            "Evitar la deshidratacion, especialmente en epocas de calor o ejercicio intenso. "
            "Consultar con el medico para evaluar posibles causas."
        ),
        rec_low=(
            "Seguir las mismas recomendaciones dieteticas que para la hemoglobina baja. "
            "Priorizar alimentos ricos en hierro, acido folico (espinacas, brocoli, esparragos) "
            "y vitamina B12 (carnes, huevos, lacteos). "
            "Mantener una hidratacion adecuada pero no excesiva."
        ),
    ),
    Marker(
        name="Leucocitos", unit="/uL",
        low_m=4500, high_m=11000, decimals=0,
        abs_min=1500, abs_max=25000,
        mimic_labels=["White Blood Cells"],
        # MIMIC WBC is in K/uL, need to multiply by 1000
        unit_conversion=1000.0,
        rec_high=(
            "Los leucocitos elevados pueden indicar infeccion o inflamacion. "
            "Aumentar el consumo de alimentos antiinflamatorios: curcuma, jengibre, frutas del bosque. "
            "Incluir acidos grasos omega-3 (pescado azul, nueces). "
            "Asegurar un descanso adecuado de 7-8 horas. "
            "Reducir el estres con tecnicas de relajacion. Consultar con el medico."
        ),
        rec_low=(
            "Priorizar la higiene alimentaria para evitar infecciones. "
            "Aumentar el consumo de proteinas de alta calidad (pollo, pescado, huevos). "
            "Incluir alimentos ricos en zinc: mariscos, semillas de calabaza, carne de ternera. "
            "Aumentar vitamina C (citricos, kiwi, pimiento rojo) y vitamina E (almendras, aceite de girasol). "
            "Evitar el contacto con personas enfermas. Consultar con el medico urgentemente si los niveles son muy bajos."
        ),
    ),
    Marker(
        name="Plaquetas", unit="/uL",
        low_m=150000, high_m=400000, decimals=0,
        abs_min=50000, abs_max=700000,
        mimic_labels=["Platelet Count"],
        # MIMIC platelets in K/uL, multiply by 1000
        unit_conversion=1000.0,
        rec_high=(
            "Aumentar alimentos ricos en omega-3 por su efecto antiagregante: "
            "salmon, sardinas, atun, semillas de lino. "
            "Incluir ajo y cebolla en la dieta diaria. "
            "Mantenerse bien hidratado. Consultar con el medico para seguimiento."
        ),
        rec_low=(
            "Incluir alimentos ricos en vitamina K: brocoli, espinacas, col rizada, kale. "
            "Aumentar el consumo de vitamina C: naranja, fresa, kiwi, pimiento. "
            "Incluir alimentos ricos en folato: esparragos, aguacate, legumbres. "
            "Evitar el alcohol. Evitar farmacos antiinflamatorios sin supervision medica. "
            "Consultar con el medico de forma urgente si hay sangrados o hematomas."
        ),
    ),
    Marker(
        name="Hierro serico", unit="ug/dL",
        low_m=60, high_m=170, decimals=0,
        abs_min=15, abs_max=300,
        mimic_labels=["Iron"],
        rec_high=(
            "Reducir el consumo de carnes rojas y visceras. "
            "Evitar suplementos de hierro y multivitaminicos con hierro. "
            "Aumentar el consumo de te y cafe con las comidas (inhiben la absorcion de hierro). "
            "Aumentar la fibra y los alimentos ricos en calcio. "
            "Donar sangre si el medico lo autoriza. Consultar para descartar hemocromatosis."
        ),
        rec_low=(
            "Aumentar carnes rojas magras (ternera, cordero), higado, morcilla. "
            "Incluir mariscos: mejillones, almejas, berberechos. "
            "Legumbres: lentejas, garbanzos, judias. Combinar siempre con vitamina C "
            "(zumo de limon, naranja, pimiento crudo). "
            "Evitar te, cafe y lacteos en las comidas principales. "
            "Cocinar en sartenes de hierro fundido."
        ),
    ),
    Marker(
        name="Ferritina", unit="ng/mL",
        low_m=20, high_m=250, low_f=10, high_f=120, decimals=1,
        abs_min=3, abs_max=500,
        mimic_labels=["Ferritin"],
        rec_high=(
            "Reducir alimentos ricos en hierro hemo: carnes rojas, visceras, mariscos. "
            "Aumentar alimentos que reducen la absorcion de hierro: lacteos, te verde, cafe. "
            "Incluir alimentos ricos en calcio con las comidas. "
            "Evitar la vitamina C con las comidas ricas en hierro. "
            "Descartar hemocromatosis y procesos inflamatorios con el medico."
        ),
        rec_low=(
            "Seguir una dieta rica en hierro: carnes rojas, higado, mejillones, lentejas. "
            "Tomar vitamina C con cada comida principal para potenciar la absorcion. "
            "Considerar suplementacion de hierro oral bajo supervision medica. "
            "En mujeres en edad fertil, revisar posibles perdidas menstruales abundantes. "
            "Evitar antiácidos y te/cafe cerca de las comidas."
        ),
    ),
    Marker(
        name="Vitamina B12", unit="pg/mL",
        low_m=200, high_m=900, decimals=0,
        abs_min=80, abs_max=1500,
        mimic_labels=["Vitamin B12"],
        rec_high=(
            "Niveles elevados raramente requieren intervencion dietetica. "
            "Suspender suplementos de B12 si se estan tomando. "
            "Consultar con el medico para descartar causas hepaticas."
        ),
        rec_low=(
            "Consumir mas alimentos ricos en B12: higado de ternera, sardinas, salmon, atun, "
            "huevos, queso, yogur, leche. "
            "En dietas vegetarianas o veganas, la suplementacion es imprescindible. "
            "Considerar suplementacion sublingual o intramuscular si la absorcion es deficiente. "
            "Incluir alimentos fermentados (chucrut, kimchi) que favorecen la salud intestinal y la absorcion."
        ),
    ),
    Marker(
        name="Vitamina D", unit="ng/mL",
        low_m=30, high_m=100, decimals=1,
        abs_min=5, abs_max=130,
        mimic_labels=["25-OH Vitamin D"],
        rec_high=(
            "Reducir o suspender la suplementacion de vitamina D. "
            "Limitar la exposicion solar directa. "
            "Reducir alimentos muy enriquecidos en vitamina D. "
            "Aumentar la hidratacion. Consultar con el medico."
        ),
        rec_low=(
            "Exponerse al sol 15-20 minutos diarios (brazos y cara), preferiblemente antes de las 12h. "
            "Consumir pescado azul 3 veces/semana: salmon, caballa, sardinas, atun. "
            "Incluir yema de huevo, quesos grasos y setas (champiñones expuestos al sol). "
            "Considerar suplementacion de vitamina D3 (colecalciferol) bajo supervision medica. "
            "Tomar la vitamina D con una comida que contenga grasa para mejorar la absorcion."
        ),
    ),
    Marker(
        name="TSH", unit="mUI/L",
        low_m=0.4, high_m=4.0, decimals=2,
        abs_min=0.01, abs_max=15.0,
        mimic_labels=["Thyroid Stimulating Hormone"],
        rec_high=(
            "TSH alta puede indicar hipotiroidismo. Asegurar un aporte adecuado de yodo: "
            "sal yodada, pescados, mariscos, algas (con moderacion). "
            "Incluir selenio: nueces de Brasil (2-3 al dia), atun, huevos. "
            "Aumentar zinc: ostras, carne de ternera, semillas de calabaza. "
            "Evitar el exceso de cruciferas crudas (brocoli, coliflor, col) ya que pueden interferir con la tiroides. "
            "Cocinar siempre las cruciferas. Consultar con endocrinologo."
        ),
        rec_low=(
            "TSH baja puede indicar hipertiroidismo. Reducir el consumo de yodo: "
            "limitar algas, mariscos y sal yodada. "
            "Aumentar alimentos ricos en calcio y vitamina D para proteger los huesos. "
            "Incluir cruciferas cocidas (brocoli, coliflor) que pueden ayudar a modular la funcion tiroidea. "
            "Evitar la cafeina y estimulantes. Mantener una ingesta calorica adecuada. "
            "Consultar urgentemente con endocrinologo."
        ),
    ),
    Marker(
        name="Creatinina", unit="mg/dL",
        low_m=0.7, high_m=1.3, decimals=2,
        abs_min=0.3, abs_max=5.0,
        mimic_labels=["Creatinine"],
        rec_high=(
            "Aumentar la hidratacion: beber 2-2.5 litros de agua al dia. "
            "Reducir el consumo de proteinas animales, especialmente carnes rojas. "
            "Limitar la sal a menos de 5 g/dia. "
            "Evitar suplementos de creatina. "
            "Incluir frutas y verduras con alto contenido en agua (sandia, pepino, apio). "
            "Reducir alimentos ricos en potasio si el medico lo indica. "
            "Consultar con nefrologo para evaluacion de funcion renal."
        ),
        rec_low=(
            "Niveles bajos de creatinina generalmente no son preocupantes. "
            "Pueden indicar baja masa muscular. Aumentar proteinas de calidad: "
            "pollo, pescado, huevos, legumbres. "
            "Incluir ejercicio de fuerza para aumentar la masa muscular. "
            "Asegurar una ingesta calorica suficiente."
        ),
    ),
    Marker(
        name="Acido urico", unit="mg/dL",
        low_m=3.5, high_m=7.2, decimals=1,
        abs_min=1.5, abs_max=14.0,
        mimic_labels=["Uric Acid"],
        rec_high=(
            "Reducir drasticamente el consumo de purinas: visceras (higado, rinones), "
            "mariscos (gambas, mejillones), carnes rojas, embutidos. "
            "Eliminar cerveza y licores. Limitar el vino a 1 copa ocasional. "
            "Beber abundante agua (minimo 2 litros/dia). "
            "Incluir cerezas y frutas del bosque (efecto antiinflamatorio). "
            "Aumentar lacteos desnatados que ayudan a eliminar acido urico. "
            "Limitar la fructosa: evitar refrescos azucarados y zumos industriales."
        ),
        rec_low=(
            "Niveles bajos de acido urico son poco frecuentes y raramente preocupantes. "
            "Asegurar una dieta equilibrada con proteinas suficientes. "
            "Consultar con el medico si hay sintomas asociados."
        ),
    ),
    Marker(
        name="ALT/GPT", unit="U/L",
        low_m=7, high_m=56, decimals=0,
        abs_min=3, abs_max=200,
        mimic_labels=["Alanine Aminotransferase (ALT)"],
        rec_high=(
            "Eliminar completamente el alcohol. "
            "Reducir alimentos ultraprocesados, frituras y grasas saturadas. "
            "Aumentar verduras de hoja verde, alcachofas y cardo mariano (infusion). "
            "Incluir alimentos ricos en antioxidantes: frutas del bosque, te verde, curcuma. "
            "Mantener un peso saludable: la grasa abdominal danña el higado. "
            "Evitar automedicacion con paracetamol y antiinflamatorios. "
            "Consultar con el medico para descartar hepatitis u otras causas."
        ),
        rec_low=(
            "Niveles bajos de ALT generalmente son normales y no requieren intervencion. "
            "Mantener una dieta equilibrada."
        ),
    ),
    Marker(
        name="AST/GOT", unit="U/L",
        low_m=10, high_m=40, decimals=0,
        abs_min=5, abs_max=180,
        mimic_labels=["Asparate Aminotransferase (AST)"],
        rec_high=(
            "Seguir las mismas recomendaciones hepatoprotectoras que para ALT elevada. "
            "Eliminar alcohol, reducir grasas saturadas y ultraprocesados. "
            "Incluir cardo mariano, alcachofa y boldo en infusiones. "
            "Aumentar vegetales cruciferos cocidos (brocoli, coliflor). "
            "Evitar el exceso de ejercicio intenso (puede elevar AST transitoriamente). "
            "Consultar con el medico."
        ),
        rec_low=(
            "Niveles bajos de AST son normales. No requieren intervencion especifica."
        ),
    ),
    Marker(
        name="GGT", unit="U/L",
        low_m=9, high_m=48, decimals=0,
        abs_min=4, abs_max=250,
        mimic_labels=["Gamma Glutamyltransferase"],
        rec_high=(
            "Eliminar totalmente el consumo de alcohol (GGT es muy sensible al alcohol). "
            "Reducir el consumo de grasas saturadas y azucares refinados. "
            "Aumentar el consumo de verduras amargas: alcachofa, endivias, rucula, diente de leon. "
            "Incluir ajo, cebolla y curcuma por sus propiedades hepatoprotectoras. "
            "Beber infusiones de cardo mariano y te verde. "
            "Mantener un peso saludable y hacer ejercicio regular."
        ),
        rec_low=(
            "Niveles bajos de GGT no son clinicamente significativos. "
            "Mantener habitos saludables."
        ),
    ),
]

MARKER_MAP = {m.name: m for m in MARKERS}

# Build reverse lookup: MIMIC label -> our Marker
MIMIC_LABEL_TO_MARKER = {}
for m in MARKERS:
    for lbl in m.mimic_labels:
        MIMIC_LABEL_TO_MARKER[lbl] = m


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_range(marker, sex):
    low = marker.low_f if (sex == "F" and marker.low_f is not None) else marker.low_m
    high = marker.high_f if (sex == "F" and marker.high_f is not None) else marker.high_m
    return low, high


def classify_value(val, marker, sex):
    low, high = get_range(marker, sex)
    if val > high:
        return "alto"
    elif val < low:
        return "bajo"
    return "normal"


def format_value(val, marker):
    if marker.decimals == 0:
        int_val = int(round(val))
        if int_val >= 10000:
            return f"{int_val:,}".replace(",", ".")
        return str(int_val)
    return f"{val:.{marker.decimals}f}"


def build_sample(patient_markers, sex):
    """
    Build a training sample from a list of (Marker, value) tuples.
    sex: 'M' or 'F'
    """
    # Assign a random age (MIMIC demo doesn't have easily accessible age)
    age = random.randint(25, 85)

    sex_label = "Hombre" if sex == "M" else "Mujer"
    input_lines = [
        f"Paciente: {sex_label}, {age} anos.",
        "Resultados de analitica de sangre:",
        "",
    ]

    values_info = []
    for marker, val in patient_markers:
        classification = classify_value(val, marker, sex)
        values_info.append((marker, val, classification))

        status = ""
        if classification == "alto":
            status = " [ALTO]"
        elif classification == "bajo":
            status = " [BAJO]"
        else:
            status = " [Normal]"
        formatted = format_value(val, marker)
        input_lines.append(f"- {marker.name}: {formatted} {marker.unit}{status}")

    input_text = "\n".join(input_lines)

    # Build output
    abnormal = [(m, v, c) for m, v, c in values_info if c != "normal"]

    if not abnormal:
        output_text = (
            "Todos los valores analizados se encuentran dentro de los rangos normales. "
            "Recomendaciones generales:\n\n"
            "- Mantener una dieta mediterranea equilibrada rica en frutas, verduras, legumbres, "
            "cereales integrales, pescado y aceite de oliva virgen extra.\n"
            "- Realizar actividad fisica moderada al menos 150 minutos a la semana.\n"
            "- Dormir entre 7 y 8 horas diarias.\n"
            "- Mantener una buena hidratacion (1.5-2 litros de agua al dia).\n"
            "- Realizar controles analiticos anuales de seguimiento."
        )
    else:
        output_parts = [
            "Basandonos en los resultados de su analitica, le proporcionamos las "
            "siguientes recomendaciones personalizadas:\n"
        ]
        for marker, val, classification in abnormal:
            formatted = format_value(val, marker)
            low, high = get_range(marker, sex)
            ref_text = f"(valor: {formatted} {marker.unit}, referencia: {format_value(low, marker)}-{format_value(high, marker)} {marker.unit})"
            if classification == "alto":
                output_parts.append(
                    f"**{marker.name} elevado/a** {ref_text}:\n{marker.rec_high}\n"
                )
            else:
                output_parts.append(
                    f"**{marker.name} bajo/a** {ref_text}:\n{marker.rec_low}\n"
                )

        output_parts.append(
            "**Recomendaciones generales adicionales:**\n"
            "- Mantener una alimentacion variada basada en la dieta mediterranea.\n"
            "- Realizar actividad fisica regular adaptada a su condicion.\n"
            "- Asegurar un descanso adecuado de 7-8 horas.\n"
            "- Acudir a revision medica para seguimiento de los valores alterados.\n"
            "- Estas recomendaciones son orientativas y no sustituyen el consejo de su medico."
        )

        output_text = "\n".join(output_parts)

    marker_names = [m.name for m, _, _ in values_info]

    return {
        "input": input_text,
        "output": output_text,
        "markers": marker_names,
    }


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def main():
    print("Loading MIMIC-IV Demo data...")
    lab = pd.read_csv(os.path.join(RAW_DIR, "labevents.csv"))
    items = pd.read_csv(os.path.join(RAW_DIR, "d_labitems.csv"))

    # Merge to get labels
    merged = lab.merge(items[["itemid", "label"]], on="itemid", how="left")

    # Filter to only our target labels
    target_labels = set(MIMIC_LABEL_TO_MARKER.keys())
    relevant = merged[merged["label"].isin(target_labels)].copy()
    relevant = relevant.dropna(subset=["valuenum"])

    print(f"Total relevant lab events with numeric values: {len(relevant)}")

    # Convert values using unit_conversion
    def convert_value(row):
        marker = MIMIC_LABEL_TO_MARKER[row["label"]]
        return row["valuenum"] * marker.unit_conversion

    relevant["converted_value"] = relevant.apply(convert_value, axis=1)

    # Group by subject_id and hadm_id (admission)
    # Each admission becomes a potential sample
    grouped = relevant.groupby(["subject_id", "hadm_id"])

    samples = []
    skipped = 0

    for (subject_id, hadm_id), group in grouped:
        # For each admission, take the first value per marker (earliest charttime)
        group_sorted = group.sort_values("charttime")

        # Deduplicate: keep first occurrence per MIMIC label
        seen_markers = set()
        patient_markers = []

        for _, row in group_sorted.iterrows():
            marker = MIMIC_LABEL_TO_MARKER[row["label"]]
            if marker.name in seen_markers:
                continue
            seen_markers.add(marker.name)

            val = row["converted_value"]

            # Sanity check: skip extreme outliers beyond abs range
            if val < marker.abs_min * 0.5 or val > marker.abs_max * 1.5:
                continue

            patient_markers.append((marker, round(val, marker.decimals)))

        # Need at least 3 markers for a useful sample
        if len(patient_markers) < 3:
            skipped += 1
            continue

        # Limit to max 8 markers (randomly select if more)
        if len(patient_markers) > 8:
            patient_markers = random.sample(patient_markers, 8)

        # Randomly assign sex (MIMIC demo doesn't easily expose gender in lab data)
        sex = random.choice(["M", "F"])

        sample = build_sample(patient_markers, sex)
        samples.append(sample)

    print(f"\nAdmissions processed: {len(samples) + skipped}")
    print(f"Samples generated: {len(samples)}")
    print(f"Skipped (too few markers): {skipped}")

    # Also generate additional samples by taking different time windows
    # within the same admission (different lab draws on different days)
    additional_samples = []

    for (subject_id, hadm_id), group in grouped:
        if len(group) < 10:
            continue

        group_sorted = group.sort_values("charttime")
        charttimes = group_sorted["charttime"].unique()

        if len(charttimes) < 4:
            continue

        # Split into time windows (roughly by quartile of charttimes)
        n = len(charttimes)
        windows = [
            charttimes[n // 4: n // 2],
            charttimes[n // 2: 3 * n // 4],
        ]

        for window_times in windows:
            window_data = group_sorted[group_sorted["charttime"].isin(window_times)]

            seen_markers = set()
            patient_markers = []
            for _, row in window_data.iterrows():
                marker = MIMIC_LABEL_TO_MARKER[row["label"]]
                if marker.name in seen_markers:
                    continue
                seen_markers.add(marker.name)
                val = row["converted_value"]
                if val < marker.abs_min * 0.5 or val > marker.abs_max * 1.5:
                    continue
                patient_markers.append((marker, round(val, marker.decimals)))

            if len(patient_markers) < 3:
                continue
            if len(patient_markers) > 8:
                patient_markers = random.sample(patient_markers, 8)

            sex = random.choice(["M", "F"])
            sample = build_sample(patient_markers, sex)
            additional_samples.append(sample)

    print(f"Additional time-window samples: {len(additional_samples)}")

    all_samples = samples + additional_samples
    random.shuffle(all_samples)

    print(f"\nTotal MIMIC samples: {len(all_samples)}")

    # Write output
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for s in all_samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    print(f"Saved to: {OUTPUT_FILE}")

    # Stats
    abnormal_count = sum(
        1 for s in all_samples
        if "[ALTO]" in s["input"] or "[BAJO]" in s["input"]
    )
    print(f"\nStats:")
    print(f"  Total samples: {len(all_samples)}")
    print(f"  Samples with abnormal values: {abnormal_count} ({abnormal_count / len(all_samples) * 100:.1f}%)")

    marker_freq = defaultdict(int)
    for s in all_samples:
        for m in s["markers"]:
            marker_freq[m] += 1
    print(f"  Marker frequency:")
    for name, count in sorted(marker_freq.items(), key=lambda x: -x[1]):
        print(f"    {name}: {count}")


if __name__ == "__main__":
    main()
