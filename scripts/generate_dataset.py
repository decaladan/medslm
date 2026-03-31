#!/usr/bin/env python3
"""
Generate synthetic training dataset for a medical AI model.
Produces blood test results in Spanish paired with personalized
diet and lifestyle recommendations.
"""

import json
import random
import os
from dataclasses import dataclass, field
from typing import Optional

SEED = 42
random.seed(SEED)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
TRAIN_FILE = os.path.join(OUTPUT_DIR, "synthetic_blood_es.jsonl")
TEST_FILE = os.path.join(OUTPUT_DIR, "synthetic_blood_es_test.jsonl")

TRAIN_SIZE = 3000
TEST_SIZE = 200


# ---------------------------------------------------------------------------
# Marker definitions
# ---------------------------------------------------------------------------

@dataclass
class Marker:
    name: str
    unit: str
    low_m: float            # lower bound (male or unisex)
    high_m: float           # upper bound (male or unisex)
    low_f: Optional[float] = None   # lower bound female (if different)
    high_f: Optional[float] = None  # upper bound female (if different)
    decimals: int = 0
    rec_high: str = ""
    rec_low: str = ""
    # for generation: plausible absolute min / max
    abs_min: float = 0.0
    abs_max: float = 0.0
    # correlated markers (name -> direction multiplier)
    correlations: dict = field(default_factory=dict)


MARKERS = [
    Marker(
        name="Glucosa",
        unit="mg/dL",
        low_m=70, high_m=100,
        decimals=0,
        abs_min=50, abs_max=350,
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
        correlations={"Trigliceridos": 0.6, "Colesterol Total": 0.3},
    ),
    Marker(
        name="Colesterol Total",
        unit="mg/dL",
        low_m=125, high_m=200,
        decimals=0,
        abs_min=90, abs_max=380,
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
        correlations={"LDL": 0.7, "Trigliceridos": 0.4},
    ),
    Marker(
        name="LDL",
        unit="mg/dL",
        low_m=50, high_m=130,
        decimals=0,
        abs_min=30, abs_max=260,
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
        correlations={"Colesterol Total": 0.7},
    ),
    Marker(
        name="HDL",
        unit="mg/dL",
        low_m=40, high_m=100,
        low_f=50, high_f=100,
        decimals=0,
        abs_min=20, abs_max=120,
        # Note: for HDL, "high" is good and "low" is bad.
        # rec_high = advice when HDL is above range (rare, usually fine)
        # rec_low  = advice when HDL is below range (common concern)
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
        name="Trigliceridos",
        unit="mg/dL",
        low_m=35, high_m=150,
        decimals=0,
        abs_min=25, abs_max=600,
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
        correlations={"Glucosa": 0.5},
    ),
    Marker(
        name="Hemoglobina",
        unit="g/dL",
        low_m=13, high_m=17,
        low_f=12, high_f=16,
        decimals=1,
        abs_min=6, abs_max=22,
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
        correlations={"Hematocrito": 0.9, "Hierro serico": 0.6, "Ferritina": 0.5},
    ),
    Marker(
        name="Hematocrito",
        unit="%",
        low_m=40, high_m=54,
        low_f=36, high_f=48,
        decimals=1,
        abs_min=20, abs_max=65,
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
        correlations={"Hemoglobina": 0.9},
    ),
    Marker(
        name="Leucocitos",
        unit="/uL",
        low_m=4500, high_m=11000,
        decimals=0,
        abs_min=1500, abs_max=25000,
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
        name="Plaquetas",
        unit="/uL",
        low_m=150000, high_m=400000,
        decimals=0,
        abs_min=50000, abs_max=700000,
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
        name="Hierro serico",
        unit="ug/dL",
        low_m=60, high_m=170,
        decimals=0,
        abs_min=15, abs_max=300,
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
        correlations={"Ferritina": 0.7, "Hemoglobina": 0.5},
    ),
    Marker(
        name="Ferritina",
        unit="ng/mL",
        low_m=20, high_m=250,
        low_f=10, high_f=120,
        decimals=1,
        abs_min=3, abs_max=500,
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
        correlations={"Hierro serico": 0.7},
    ),
    Marker(
        name="Vitamina B12",
        unit="pg/mL",
        low_m=200, high_m=900,
        decimals=0,
        abs_min=80, abs_max=1500,
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
        name="Vitamina D",
        unit="ng/mL",
        low_m=30, high_m=100,
        decimals=1,
        abs_min=5, abs_max=130,
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
        name="TSH",
        unit="mUI/L",
        low_m=0.4, high_m=4.0,
        decimals=2,
        abs_min=0.01, abs_max=15.0,
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
        name="Creatinina",
        unit="mg/dL",
        low_m=0.7, high_m=1.3,
        decimals=2,
        abs_min=0.3, abs_max=5.0,
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
        name="Acido urico",
        unit="mg/dL",
        low_m=3.5, high_m=7.2,
        decimals=1,
        abs_min=1.5, abs_max=14.0,
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
        name="ALT/GPT",
        unit="U/L",
        low_m=7, high_m=56,
        decimals=0,
        abs_min=3, abs_max=200,
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
        correlations={"AST/GOT": 0.7, "GGT": 0.5},
    ),
    Marker(
        name="AST/GOT",
        unit="U/L",
        low_m=10, high_m=40,
        decimals=0,
        abs_min=5, abs_max=180,
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
        correlations={"ALT/GPT": 0.7, "GGT": 0.5},
    ),
    Marker(
        name="GGT",
        unit="U/L",
        low_m=9, high_m=48,
        decimals=0,
        abs_min=4, abs_max=250,
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
        correlations={"ALT/GPT": 0.5, "AST/GOT": 0.5},
    ),
]

MARKER_MAP = {m.name: m for m in MARKERS}


# ---------------------------------------------------------------------------
# Value generation helpers
# ---------------------------------------------------------------------------

def get_range(marker: Marker, sex: str):
    """Return (low, high) for a marker given sex."""
    low = marker.low_f if (sex == "F" and marker.low_f is not None) else marker.low_m
    high = marker.high_f if (sex == "F" and marker.high_f is not None) else marker.high_m
    return low, high


def generate_value(marker: Marker, sex: str, category: str) -> float:
    """Generate a value for a given category: normal, high, low, borderline_high, borderline_low."""
    low, high = get_range(marker, sex)
    span = high - low

    if category == "normal":
        # comfortably inside range
        val = random.uniform(low + span * 0.1, high - span * 0.1)
    elif category == "high":
        val = random.uniform(high * 1.05, min(high * 1.6, marker.abs_max))
    elif category == "low":
        val = random.uniform(max(low * 0.4, marker.abs_min), low * 0.95)
    elif category == "borderline_high":
        val = random.uniform(high * 0.95, high * 1.08)
    elif category == "borderline_low":
        val = random.uniform(low * 0.92, low * 1.08)
    else:
        val = random.uniform(low, high)

    return round(val, marker.decimals)


def classify_value(val: float, marker: Marker, sex: str) -> str:
    """Classify a value as normal/alto/bajo."""
    low, high = get_range(marker, sex)
    if val > high:
        return "alto"
    elif val < low:
        return "bajo"
    return "normal"


# ---------------------------------------------------------------------------
# Sample generation
# ---------------------------------------------------------------------------

def pick_categories(n_markers: int) -> list[str]:
    """Pick value categories for n markers. ~60% normal, 25% abnormal, 15% borderline."""
    cats = []
    for _ in range(n_markers):
        r = random.random()
        if r < 0.60:
            cats.append("normal")
        elif r < 0.72:
            cats.append("high")
        elif r < 0.85:
            cats.append("low")
        elif r < 0.925:
            cats.append("borderline_high")
        else:
            cats.append("borderline_low")
    return cats


def apply_correlations(selected_markers: list[Marker], categories: list[str]):
    """If a marker is abnormal and has correlations, bias correlated markers."""
    name_to_idx = {m.name: i for i, m in enumerate(selected_markers)}

    for i, marker in enumerate(selected_markers):
        if categories[i] in ("normal", "borderline_low", "borderline_high"):
            continue
        for corr_name, strength in marker.correlations.items():
            if corr_name in name_to_idx:
                j = name_to_idx[corr_name]
                if categories[j] == "normal" and random.random() < strength:
                    # push correlated marker in the same direction
                    categories[j] = categories[i]


def format_value(val: float, marker: Marker) -> str:
    """Format a numeric value for display."""
    if marker.decimals == 0:
        int_val = int(val)
        # Use thousands separator for large numbers
        if int_val >= 10000:
            return f"{int_val:,}".replace(",", ".")
        return str(int_val)
    return f"{val:.{marker.decimals}f}"


def generate_sample() -> dict:
    """Generate a single training sample."""
    sex = random.choice(["M", "F"])
    age = random.randint(18, 85)

    n_markers = random.randint(4, 8)
    selected = random.sample(MARKERS, n_markers)
    categories = pick_categories(n_markers)
    apply_correlations(selected, categories)

    # Generate values
    values = []
    for marker, cat in zip(selected, categories):
        val = generate_value(marker, sex, cat)
        classification = classify_value(val, marker, sex)
        values.append((marker, val, classification))

    # Build input text
    sex_label = "Hombre" if sex == "M" else "Mujer"
    input_lines = [
        f"Paciente: {sex_label}, {age} anos.",
        "Resultados de analitica de sangre:",
        "",
    ]
    for marker, val, classification in values:
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

    # Build output text (recommendations)
    abnormal = [(m, v, c) for m, v, c in values if c != "normal"]

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
        output_parts = []
        output_parts.append(
            "Basandonos en los resultados de su analitica, le proporcionamos las "
            "siguientes recomendaciones personalizadas:\n"
        )
        for marker, val, classification in abnormal:
            formatted = format_value(val, marker)
            low, high = get_range(marker, sex)
            if classification == "alto":
                ref_text = f"(valor: {formatted} {marker.unit}, referencia: {format_value(low, marker)}-{format_value(high, marker)} {marker.unit})"
                output_parts.append(
                    f"**{marker.name} elevado/a** {ref_text}:\n{marker.rec_high}\n"
                )
            else:
                ref_text = f"(valor: {formatted} {marker.unit}, referencia: {format_value(low, marker)}-{format_value(high, marker)} {marker.unit})"
                output_parts.append(
                    f"**{marker.name} bajo/a** {ref_text}:\n{marker.rec_low}\n"
                )

        # General closing advice
        output_parts.append(
            "**Recomendaciones generales adicionales:**\n"
            "- Mantener una alimentacion variada basada en la dieta mediterranea.\n"
            "- Realizar actividad fisica regular adaptada a su condicion.\n"
            "- Asegurar un descanso adecuado de 7-8 horas.\n"
            "- Acudir a revision medica para seguimiento de los valores alterados.\n"
            "- Estas recomendaciones son orientativas y no sustituyen el consejo de su medico."
        )

        output_text = "\n".join(output_parts)

    marker_names = [m.name for m, _, _ in values]

    return {
        "input": input_text,
        "output": output_text,
        "markers": marker_names,
    }


def write_jsonl(path: str, samples: list[dict]):
    """Write samples to a JSONL file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")


def main():
    print(f"Generating {TRAIN_SIZE} training samples...")
    random.seed(SEED)
    train_samples = [generate_sample() for _ in range(TRAIN_SIZE)]

    print(f"Generating {TEST_SIZE} test samples...")
    random.seed(SEED + 1)
    test_samples = [generate_sample() for _ in range(TEST_SIZE)]

    write_jsonl(TRAIN_FILE, train_samples)
    print(f"Training set saved to: {TRAIN_FILE}")

    write_jsonl(TEST_FILE, test_samples)
    print(f"Test set saved to:     {TEST_FILE}")

    # Quick stats
    abnormal_count = sum(
        1 for s in train_samples
        if "[ALTO]" in s["input"] or "[BAJO]" in s["input"]
    )
    print(f"\nStats (training set):")
    print(f"  Total samples: {len(train_samples)}")
    print(f"  Samples with abnormal values: {abnormal_count} ({abnormal_count/len(train_samples)*100:.1f}%)")

    # Count marker frequency
    marker_freq: dict[str, int] = {}
    for s in train_samples:
        for m in s["markers"]:
            marker_freq[m] = marker_freq.get(m, 0) + 1
    print(f"  Marker frequency (top 5):")
    for name, count in sorted(marker_freq.items(), key=lambda x: -x[1])[:5]:
        print(f"    {name}: {count}")


if __name__ == "__main__":
    main()
