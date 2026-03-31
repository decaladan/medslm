"""
v2 Dataset Generator - Knowledge Distillation
High-quality, natural Spanish medical recommendations for blood test analysis.
Multiple response variations, natural doctor-like tone, proper medical reasoning.
"""
import json
import random
import os

random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# ============================================================
# MARKER DEFINITIONS with reference ranges
# ============================================================
MARKERS = {
    "Glucosa": {
        "unit": "mg/dL",
        "range_m": (70, 100), "range_f": (70, 100),
        "low_range": (45, 69), "high_range": (101, 250), "borderline_high": (101, 115), "borderline_low": (65, 69),
    },
    "Colesterol Total": {
        "unit": "mg/dL",
        "range_m": (125, 199), "range_f": (125, 199),
        "low_range": (80, 124), "high_range": (200, 300), "borderline_high": (200, 220), "borderline_low": (110, 124),
    },
    "LDL": {
        "unit": "mg/dL",
        "range_m": (50, 129), "range_f": (50, 129),
        "low_range": (20, 49), "high_range": (130, 220), "borderline_high": (130, 145), "borderline_low": (40, 49),
    },
    "HDL": {
        "unit": "mg/dL",
        "range_m": (40, 80), "range_f": (50, 90),
        "low_range": (20, 39), "high_range": (81, 110), "borderline_low_m": (35, 39), "borderline_low_f": (45, 49),
    },
    "Trigliceridos": {
        "unit": "mg/dL",
        "range_m": (35, 149), "range_f": (35, 149),
        "low_range": (20, 34), "high_range": (150, 400), "borderline_high": (150, 180), "borderline_low": (25, 34),
    },
    "Hemoglobina": {
        "unit": "g/dL",
        "range_m": (13.0, 17.0), "range_f": (12.0, 16.0),
        "low_range_m": (8.0, 12.9), "low_range_f": (7.5, 11.9),
        "high_range_m": (17.1, 20.0), "high_range_f": (16.1, 19.0),
    },
    "Hematocrito": {
        "unit": "%",
        "range_m": (40.0, 54.0), "range_f": (36.0, 48.0),
        "low_range_m": (28.0, 39.9), "low_range_f": (25.0, 35.9),
        "high_range_m": (54.1, 62.0), "high_range_f": (48.1, 58.0),
    },
    "Leucocitos": {
        "unit": "/uL",
        "range_m": (4500, 11000), "range_f": (4500, 11000),
        "low_range": (2000, 4499), "high_range": (11001, 20000),
    },
    "Plaquetas": {
        "unit": "/uL",
        "range_m": (150000, 400000), "range_f": (150000, 400000),
        "low_range": (80000, 149999), "high_range": (400001, 600000),
    },
    "Hierro serico": {
        "unit": "ug/dL",
        "range_m": (60, 170), "range_f": (60, 170),
        "low_range": (20, 59), "high_range": (171, 250),
    },
    "Ferritina": {
        "unit": "ng/mL",
        "range_m": (20, 250), "range_f": (10, 120),
        "low_range_m": (5, 19), "low_range_f": (3, 9),
        "high_range_m": (251, 500), "high_range_f": (121, 350),
    },
    "Vitamina B12": {
        "unit": "pg/mL",
        "range_m": (200, 900), "range_f": (200, 900),
        "low_range": (100, 199), "high_range": (901, 1500),
    },
    "Vitamina D": {
        "unit": "ng/mL",
        "range_m": (30, 100), "range_f": (30, 100),
        "low_range": (8, 29), "high_range": (101, 150),
    },
    "TSH": {
        "unit": "mUI/L",
        "range_m": (0.4, 4.0), "range_f": (0.4, 4.0),
        "low_range": (0.05, 0.39), "high_range": (4.1, 15.0),
    },
    "Creatinina": {
        "unit": "mg/dL",
        "range_m": (0.7, 1.3), "range_f": (0.6, 1.1),
        "low_range_m": (0.3, 0.69), "low_range_f": (0.2, 0.59),
        "high_range_m": (1.31, 3.0), "high_range_f": (1.11, 2.5),
    },
    "Acido urico": {
        "unit": "mg/dL",
        "range_m": (3.5, 7.2), "range_f": (2.5, 6.0),
        "low_range": (1.0, 2.4), "high_range_m": (7.3, 12.0), "high_range_f": (6.1, 10.0),
    },
    "ALT (GPT)": {
        "unit": "U/L",
        "range_m": (7, 56), "range_f": (7, 56),
        "high_range": (57, 200),
    },
    "AST (GOT)": {
        "unit": "U/L",
        "range_m": (10, 40), "range_f": (10, 40),
        "high_range": (41, 180),
    },
    "GGT": {
        "unit": "U/L",
        "range_m": (9, 48), "range_f": (9, 48),
        "high_range": (49, 300),
    },
}

# ============================================================
# RICH RECOMMENDATIONS - Multiple variations per condition
# Written as a doctor would explain to a patient
# ============================================================

RECOMMENDATIONS = {
    "Glucosa_high": [
        """Tu nivel de glucosa esta por encima del rango normal, lo que puede indicar resistencia a la insulina o prediabetes.

Alimentacion:
- Prioriza alimentos con indice glucemico bajo: legumbres (lentejas, garbanzos), verduras de hoja verde, frutos secos.
- Sustituye el pan blanco y la pasta refinada por sus versiones integrales.
- Incluye proteina en cada comida (huevos, pescado, pollo) para estabilizar los niveles de azucar.
- Evita zumos de fruta (incluso naturales), refrescos y dulces.
- El vinagre de manzana antes de las comidas puede ayudar a moderar los picos de glucosa.

Habitos:
- Camina al menos 30 minutos despues de las comidas principales, esto reduce significativamente los picos de glucosa.
- Intenta cenar al menos 3 horas antes de dormir.
- El estres cronico eleva la glucosa: considera tecnicas de relajacion.""",

        """Los valores de glucosa elevados merecen atencion. No significa necesariamente diabetes, pero si que tu cuerpo esta teniendo dificultades para gestionar el azucar.

Que comer:
- Empieza las comidas con verdura o ensalada (la fibra ralentiza la absorcion de azucar).
- Anade canela a tus comidas: hay evidencia de que mejora la sensibilidad a la insulina.
- Aumenta el consumo de pescado azul (salmon, sardinas) 3 veces por semana.
- Las nueces, almendras y semillas de chia son excelentes snacks que no disparan la glucosa.
- Reduce drasticamente los ultraprocesados y la bolleria industrial.

Que hacer:
- El ejercicio es tan efectivo como algunos farmacos: 150 minutos semanales de actividad moderada.
- Duerme entre 7-8 horas; la falta de sueno empeora la resistencia a la insulina.
- Seria conveniente repetir la analitica en 3 meses para ver la tendencia.""",

        """Una glucosa elevada es una senal de alerta que merece atencion, pero con cambios en la alimentacion y el estilo de vida se puede corregir en muchos casos.

Recomendaciones dieteticas:
- Elimina o reduce al minimo azucares anadidos y harinas refinadas.
- Basa tu alimentacion en verduras, proteinas de calidad y grasas saludables (aceite de oliva, aguacate).
- Las legumbres son tu mejor aliado: tienen un indice glucemico bajo y mucha fibra.
- Come en plato pequeno y mastica despacio; la saciedad tarda 20 minutos en llegar.
- La avena integral en el desayuno, con frutos secos, es una opcion excelente.

Estilo de vida:
- Muevete despues de cada comida, aunque sean 10 minutos.
- Gestiona el estres: el cortisol elevado sube la glucosa directamente.
- Controla tu peso: perder un 5-7% del peso corporal mejora drasticamente la sensibilidad a la insulina.""",
    ],

    "Glucosa_low": [
        """Tu glucosa esta ligeramente por debajo del rango normal. Esto puede causar fatiga, mareos o dificultad para concentrarte.

Alimentacion:
- No saltes comidas: haz 5 comidas al dia (3 principales y 2 tentempiés).
- Incluye siempre carbohidratos complejos (arroz integral, pan integral, patata) en cada comida.
- Combina los carbohidratos con proteina y grasa para una liberacion de energia mas estable.
- Ten a mano fruta seca o frutos secos por si sientes bajones de energia.
- Evita el ayuno prolongado.

Habitos:
- Si haces ejercicio intenso, come algo antes y despues.
- El alcohol con el estomago vacio puede provocar hipoglucemias: evitalo.
- Consulta con tu medico si los episodios de bajada de azucar son frecuentes.""",
    ],

    "Colesterol Total_high": [
        """Tu colesterol total esta elevado. Es importante mirar el desglose (LDL y HDL) para entender el riesgo real, pero en general conviene actuar.

Alimentacion cardiosaludable:
- Aceite de oliva virgen extra como grasa principal (2-3 cucharadas al dia).
- Pescado azul 3-4 veces por semana: salmon, sardinas, caballa, anchoas.
- Reduce carnes rojas a 1-2 veces por semana maximo; prioriza carnes blancas y legumbres.
- Aumenta la fibra soluble: avena, manzanas, zanahorias, legumbres. La fibra atrapa el colesterol en el intestino.
- Un punado de nueces al dia (30g) puede reducir el LDL un 5-10%.
- Evita la bolleria industrial, margarinas y alimentos con grasas trans.

Estilo de vida:
- El ejercicio aerobico regular (caminar rapido, nadar, bicicleta) sube el HDL y baja el LDL.
- Si fumas, dejarlo es lo mas impactante que puedes hacer por tu perfil lipidico.
- Mantener un peso saludable es clave: el exceso de grasa abdominal empeora el colesterol.""",
    ],

    "LDL_high": [
        """El LDL (colesterol "malo") esta por encima de lo deseable. Es el principal factor de riesgo cardiovascular modificable con dieta.

Estrategia nutricional:
- Reduce las grasas saturadas: menos embutidos, quesos curados, mantequilla y carnes grasas.
- Sustituye por grasas insaturadas: aceite de oliva, aguacate, frutos secos, pescado azul.
- Los esteroles vegetales (presentes en algunos yogures y margarinas funcionales) pueden reducir el LDL un 10%.
- La fibra soluble es tu gran aliada: avena con beta-glucanos, legumbres, frutas con piel.
- Anade semillas de lino molidas a tus comidas (ricas en omega-3 vegetal).
- Los tomates cocinados (licopeno) y el ajo tienen efecto protector cardiovascular.

Importante:
- No se trata solo de evitar grasas: los azucares y carbohidratos refinados tambien elevan el LDL indirectamente.
- Haz ejercicio aerobico al menos 5 dias por semana, 30-45 minutos.
- Repite la analitica en 3-6 meses para evaluar si los cambios estan funcionando.""",
    ],

    "HDL_low": [
        """Tu HDL (colesterol "bueno") esta bajo. El HDL es protector cardiovascular: recoge el colesterol de las arterias y lo lleva al higado para eliminarlo.

Como subirlo:
- Ejercicio aerobico regular: es lo mas efectivo para subir el HDL. 30-40 minutos al dia, 5 dias por semana.
- Aceite de oliva virgen extra: 3-4 cucharadas al dia.
- Pescado azul rico en omega-3: salmon, sardinas, caballa, atun (3-4 veces/semana).
- Un punado diario de nueces, almendras o pistachos.
- Aguacate: medio aguacate al dia aporta grasas monoinsaturadas que suben el HDL.

Que evitar:
- Las grasas trans (bolleria industrial, comida rapida) bajan activamente el HDL.
- Fumar reduce el HDL; dejarlo lo sube significativamente.
- El exceso de carbohidratos refinados baja el HDL y sube los trigliceridos.
- El sedentarismo es el enemigo numero uno del HDL.""",
    ],

    "Trigliceridos_high": [
        """Los trigliceridos elevados estan muy ligados a la alimentacion y responden muy bien a cambios dieteticos.

Alimentacion:
- Reduce drasticamente el azucar: refrescos, zumos, dulces, bolleria. El azucar se convierte directamente en trigliceridos.
- Limita el alcohol: incluso cantidades moderadas elevan los trigliceridos significativamente.
- Aumenta el omega-3: pescado azul (salmon, sardinas, caballa) 3-4 veces por semana.
- Sustituye carbohidratos refinados por integrales y legumbres.
- Las semillas de chia y lino son ricas en omega-3 vegetal.

Habitos:
- La perdida de peso, incluso modesta (3-5 kg), reduce los trigliceridos de forma notable.
- Haz ejercicio regular: 30 minutos diarios de actividad moderada.
- Evita las cenas copiosas y ricas en carbohidratos.
- El ayuno intermitente puede ayudar, pero consultalo primero con tu medico.""",
    ],

    "Hemoglobina_low": [
        """Tu hemoglobina esta baja, lo que indica anemia. Esto explica sintomas como cansancio, palidez, falta de aire o dificultad para concentrarte.

Alimentacion rica en hierro:
- Carnes rojas magras 2-3 veces por semana (ternera, cordero): contienen hierro hemo, el de mejor absorcion.
- Mariscos: mejillones, almejas y berberechos son extraordinariamente ricos en hierro.
- Higado de ternera o pollo: uno de los alimentos mas ricos en hierro que existen.
- Legumbres (lentejas, garbanzos) combinadas con vitamina C (limon, pimiento, naranja) para mejorar la absorcion.
- Espinacas, acelgas y brocoli como acompanamiento habitual.

Trucos de absorcion:
- Toma vitamina C (un zumo de naranja natural) junto con las comidas ricas en hierro.
- NO tomes te, cafe o lacteos durante las comidas principales: inhiben la absorcion del hierro.
- El calcio compite con el hierro: separa los lacteos de las comidas principales.
- Cocina en sarten de hierro: libera trazas de hierro a los alimentos.

Es importante que tu medico determine la causa de la anemia (deficit de hierro, B12, acido folico u otras causas).""",
    ],

    "Hemoglobina_high": [
        """La hemoglobina esta por encima del rango normal. Esto puede deberse a deshidratacion, tabaquismo, vivir en altitud o condiciones mas especificas.

Recomendaciones:
- Aumenta la ingesta de liquidos: al menos 2 litros de agua al dia, mas si haces ejercicio o hace calor.
- Si fumas, considera dejarlo: el tabaco eleva la hemoglobina como mecanismo compensatorio.
- Evita suplementos de hierro a menos que tu medico los prescriba especificamente.
- Consulta con tu medico para descartar causas que requieran seguimiento.

Alimentacion:
- Mantén una dieta equilibrada sin exceso de carnes rojas.
- El te y el cafe con las comidas pueden reducir ligeramente la absorcion de hierro.""",
    ],

    "Vitamina D_low": [
        """Tu vitamina D esta baja, algo muy comun pero importante de corregir. La vitamina D es esencial para los huesos, el sistema inmune y el estado de animo.

Exposicion solar:
- 15-20 minutos de sol directo al dia en brazos y cara (sin protector solar en ese periodo).
- Mejor antes de las 12h o despues de las 16h para equilibrar beneficio y riesgo.
- En invierno o en latitudes altas, la sintesis cutanea es insuficiente.

Alimentacion:
- Pescado azul graso: salmon, caballa, sardinas, atun (3-4 raciones/semana).
- Yemas de huevo: incluye 1-2 huevos al dia.
- Setas y champiñones expuestos al sol (producen vitamina D2).
- Alimentos enriquecidos: algunas leches, cereales y zumos.

Suplementacion:
- Con estos niveles, probablemente necesites un suplemento de vitamina D3 (colecalciferol).
- Toma el suplemento con la comida que contenga mas grasa del dia (la vitamina D es liposoluble).
- Tu medico determinara la dosis adecuada (habitualmente 1000-4000 UI/dia segun el deficit).
- Repite la analitica en 3 meses para verificar que los niveles suben.""",
    ],

    "Vitamina B12_low": [
        """La vitamina B12 esta por debajo del rango normal. Este deficit puede causar fatiga, problemas de memoria, hormigueos en manos y pies, e incluso anemia.

Alimentacion rica en B12:
- Higado y visceras: la fuente mas concentrada de B12 que existe.
- Mariscos: almejas, mejillones y ostras tienen cantidades extraordinarias.
- Pescado: sardinas, salmon, atun, trucha.
- Carne de ternera y cordero.
- Huevos: especialmente la yema (1-2 al dia).
- Lacteos: yogur, queso, leche.

Importante saber:
- Si sigues una dieta vegetariana o vegana, la suplementacion es imprescindible ya que la B12 solo se encuentra de forma natural en alimentos de origen animal.
- La absorcion de B12 disminuye con la edad y con ciertos medicamentos (omeprazol, metformina).
- Tu medico puede recomendar suplementacion oral o inyectable segun la causa del deficit.
- El acido folico puede enmascarar la deficiencia de B12: no te suplementes con folico sin verificar la B12.""",
    ],

    "Hierro serico_low": [
        """Tu hierro en sangre esta bajo. Junto con la ferritina, nos indica las reservas de hierro de tu cuerpo.

Alimentacion:
- Prioriza el hierro hemo (de origen animal): carnes rojas, higado, mariscos de concha (mejillones, almejas).
- Complementa con hierro no hemo (vegetal): lentejas, espinacas, garbanzos, tofu.
- Siempre acompana los alimentos ricos en hierro vegetal con vitamina C: un chorrito de limon, pimiento crudo, naranja de postre.
- La remolacha, las semillas de calabaza y los pistachos tambien son buenas fuentes.

Inhibidores de absorcion (evitar durante las comidas):
- Cafe y te: los taninos bloquean la absorcion del hierro hasta un 60%.
- Lacteos: el calcio compite directamente con el hierro.
- Cereales integrales sin remojar: los fitatos reducen la absorcion (remoja las legumbres antes de cocinar).

Tu medico valorara si necesitas suplementacion de hierro oral.""",
    ],

    "Ferritina_low": [
        """La ferritina baja indica que tus reservas de hierro estan agotadas, incluso aunque la hemoglobina pueda estar aun normal. Es una senal temprana de que el cuerpo necesita mas hierro.

Las recomendaciones son las mismas que para el hierro bajo:
- Carnes rojas magras 2-3 veces por semana, mariscos de concha, higado.
- Legumbres con limon, espinacas, frutos secos.
- Vitamina C en cada comida para potenciar la absorcion.
- Separar los lacteos y el cafe de las comidas principales.

Ademas:
- La ferritina tarda mas en recuperarse que la hemoglobina; es un proceso de semanas o meses.
- La suplementacion con hierro suele ser necesaria: consultalo con tu medico.
- Repite la analitica en 2-3 meses para verificar la recuperacion.""",
    ],

    "TSH_high": [
        """Tu TSH esta elevada, lo que sugiere que tu tiroides puede estar funcionando mas lento de lo normal (hipotiroidismo). Esto se asocia con cansancio, aumento de peso, frio, piel seca y estreñimiento.

Alimentacion para apoyar la tiroides:
- Asegura un aporte adecuado de yodo: pescado, marisco, algas (con moderacion), sal yodada.
- Selenio: fundamental para la conversion de T4 a T3. Fuentes: nueces de Brasil (2-3 al dia son suficientes), atun, huevos.
- Zinc: carnes, semillas de calabaza, garbanzos.
- Evita el exceso de soja y cruciferas crudas (brocoli, coliflor, col) ya que pueden interferir con la funcion tiroidea en grandes cantidades. Cocinadas no hay problema.

Importante:
- Estas recomendaciones no sustituyen el tratamiento medico. Si la TSH es significativamente alta, tu medico valorara tratamiento con levotiroxina.
- Repite la analitica incluyendo T4 libre y anticuerpos antitiroideos para completar el estudio.""",
    ],

    "TSH_low": [
        """Tu TSH esta baja, lo que puede indicar hipertiroidismo (tiroides acelerada). Los sintomas incluyen perdida de peso, nerviosismo, palpitaciones, temblores y sudoracion excesiva.

Recomendaciones:
- Aumenta la ingesta calorica si has perdido peso: necesitas mas energia cuando la tiroides esta acelerada.
- Calcio y vitamina D: el hipertiroidismo puede afectar a los huesos. Asegura un buen aporte de lacteos, sardinas con espina, brocoli.
- Evita la cafeina y los estimulantes: pueden empeorar la ansiedad y las palpitaciones.
- Las cruciferas (brocoli, coliflor, col) en este caso pueden ser beneficiosas, ya que ralentizan ligeramente la tiroides.

Muy importante:
- Consulta con tu medico urgentemente si tienes sintomas. El hipertiroidismo requiere evaluacion medica.
- Se necesitan pruebas adicionales: T4 libre, T3, anticuerpos.""",
    ],

    "Creatinina_high": [
        """La creatinina elevada puede indicar que los rinones no estan filtrando con toda su eficiencia. Es importante contextualizar este valor con tu masa muscular y nivel de actividad.

Recomendaciones para proteger la funcion renal:
- Hidratacion: bebe al menos 1.5-2 litros de agua al dia (salvo indicacion medica contraria).
- Modera la proteina: no eliminarla, pero evitar dietas hiperproteicas. Prioriza proteina de pescado y vegetal sobre la carne roja.
- Reduce la sal: no mas de 5g al dia. Evita embutidos, conservas, snacks salados y comida preparada.
- Controla la tension arterial y la glucosa: son los dos grandes enemigos del rinon.
- Evita antiinflamatorios (ibuprofeno, naproxeno) sin consultar al medico: son toxicos para el rinon.

Tu medico deberia valorar la tasa de filtracion glomerular (TFG) para tener una vision mas completa de la funcion renal.""",
    ],

    "Acido urico_high": [
        """El acido urico elevado aumenta el riesgo de gota (dolor articular intenso) y puede asociarse a problemas renales y cardiovasculares.

Alimentacion:
- Reduce las purinas: limita visceras (higado, rinones), mariscos (gambas, langostinos), carnes rojas y embutidos.
- El alcohol, especialmente la cerveza, eleva mucho el acido urico. Reduce o elimina su consumo.
- Los refrescos azucarados y la fructosa elevan el acido urico: eliminados.
- Aumenta los lacteos desnatados: tienen efecto protector (reducen el acido urico).
- Bebe abundante agua: al menos 2 litros al dia para facilitar la eliminacion renal del acido urico.
- Las cerezas y los frutos rojos tienen propiedades antiinflamatorias utiles en la gota.
- El cafe (con moderacion) se asocia a menores niveles de acido urico.

Verduras ricas en purinas como espinacas, esparragos y champiñones NO aumentan el riesgo de gota segun los estudios mas recientes; puedes comerlas con normalidad.""",
    ],

    "ALT (GPT)_high": [
        """Las transaminasas ALT elevadas indican que el higado esta sufriendo algun tipo de inflamacion o dano celular.

Recomendaciones para el higado:
- Elimina o reduce al minimo el alcohol: es la causa mas frecuente de dano hepatico.
- Reduce los ultraprocesados, frituras y grasas saturadas.
- El higado graso no alcoholico esta muy asociado al exceso de azucar y carbohidratos refinados: reducelos.
- Aumenta las verduras cruciferas (brocoli, coliflor, col rizada): apoyan la detoxificacion hepatica.
- El cafe (2-3 tazas al dia) tiene efecto hepatoprotector demostrado.
- Alcachofa y cardo mariano son remedios tradicionales con cierta evidencia de apoyo hepatico.
- Pierde peso si tienes sobrepeso: la grasa abdominal se acumula en el higado.

Importante:
- Revisa tus medicamentos con el medico: muchos farmacos pueden elevar las transaminasas (paracetamol, estatinas, antiinflamatorios).
- Si las transaminasas son muy altas o persisten elevadas, se necesitan mas pruebas (ecografia hepatica, serologias virales).""",
    ],

    "AST (GOT)_high": [
        """La AST elevada puede indicar dano hepatico, aunque tambien se eleva con dano muscular o cardiaco.

Las recomendaciones son similares a las de la ALT elevada:
- Reduce el consumo de alcohol y ultraprocesados.
- Dieta rica en verduras, frutas y proteinas de calidad.
- El cafe tiene efecto protector sobre el higado.
- Manten un peso saludable.

Si haces ejercicio intenso, la AST puede elevarse por dano muscular normal; en ese caso no es preocupante. Comentalo con tu medico para interpretar el valor en contexto.""",
    ],

    "GGT_high": [
        """La GGT elevada es un marcador sensible de dano hepatico y esta muy asociada al consumo de alcohol.

Recomendaciones:
- Si consumes alcohol, reducirlo o eliminarlo es lo mas importante. La GGT baja rapidamente al dejar el alcohol.
- Reduce grasas saturadas y ultraprocesados.
- Manten un peso saludable: la obesidad y el higado graso elevan la GGT.
- Revisa tu medicacion con el medico: anticonvulsivantes, anticonceptivos y algunos farmacos elevan la GGT.
- Dieta mediterranea rica en verduras, pescado, aceite de oliva y frutos secos.
- El te verde tiene propiedades antioxidantes beneficiosas para el higado.""",
    ],

    "Leucocitos_high": [
        """Los leucocitos elevados (leucocitosis) indican que tu sistema inmunitario esta activado. Puede deberse a una infeccion, inflamacion, estres o ejercicio reciente.

Recomendaciones:
- Si tienes sintomas de infeccion (fiebre, dolor, malestar), consulta con tu medico.
- Alimentos antiinflamatorios: frutas y verduras ricas en antioxidantes, pescado azul, aceite de oliva, curcuma, jengibre.
- Reduce el estres cronico: puede mantener los leucocitos elevados.
- Duerme bien: el sistema inmune se regula durante el sueno.
- Evita el tabaco: causa inflamacion cronica y eleva los leucocitos.

Si no hay sintomas aparentes y los leucocitos estan solo ligeramente elevados, probablemente se normalizaran solos. Repite la analitica en unas semanas.""",
    ],

    "Leucocitos_low": [
        """Los leucocitos bajos (leucopenia) indican que tu sistema inmunitario puede estar debilitado, lo que te hace mas vulnerable a infecciones.

Recomendaciones para fortalecer el sistema inmune:
- Alimentacion variada y rica en nutrientes: frutas, verduras, proteinas de calidad.
- Vitamina C: citricos, kiwi, pimiento rojo, fresa.
- Zinc: carnes, semillas de calabaza, garbanzos, ostras.
- Vitamina D: exposicion solar y suplementacion si es necesario.
- Probioticos: yogur natural, kefir, chucrut. El 70% del sistema inmune esta en el intestino.
- Duerme 7-8 horas: el sueno es critico para la funcion inmune.

Precauciones:
- Extrema la higiene de manos y la seguridad alimentaria.
- Evita el contacto cercano con personas enfermas.
- Consulta con tu medico para investigar la causa (farmacos, infecciones virales, etc.).""",
    ],

    "Plaquetas_low": [
        """Las plaquetas bajas (trombocitopenia) pueden aumentar el riesgo de sangrado y moratones.

Recomendaciones:
- Alimentos ricos en vitamina K (importante para la coagulacion): espinacas, brocoli, col rizada, acelgas.
- Acido folico: legumbres, verduras de hoja verde, esparragos.
- Vitamina B12: carnes, huevos, lacteos.
- Evita el alcohol: deprime la produccion de plaquetas en la medula osea.
- Evita la aspirina y los antiinflamatorios sin consultar al medico.

Precauciones:
- Cuidado con actividades de riesgo de lesion o sangrado.
- Usa cepillo de dientes suave.
- Consulta con tu medico, especialmente si las plaquetas son muy bajas o tienes sangrados espontaneos.""",
    ],

    "Plaquetas_high": [
        """Las plaquetas elevadas (trombocitosis) pueden ser reactivas (por infeccion, inflamacion, deficit de hierro) o primarias.

Recomendaciones:
- Mantente bien hidratado: la deshidratacion espesa la sangre.
- Alimentos con propiedades antiagregantes naturales: ajo, cebolla, jengibre, curcuma, pescado azul rico en omega-3.
- Modera el consumo de vitamina K en exceso (no eliminarla, pero no suplementarla).
- Ejercicio regular moderado: mejora la circulacion.
- Evita el tabaco: aumenta el riesgo de trombosis.

Tu medico deberia investigar la causa de la elevacion, especialmente si es marcada o persistente.""",
    ],
}

# ============================================================
# NORMAL RESULTS - Varied positive feedback templates
# ============================================================
NORMAL_RESPONSES = [
    """Todos los valores analizados se encuentran dentro de los rangos normales. Tus resultados reflejan un buen estado de salud general.

Recomendaciones para mantener estos buenos resultados:
- Sigue con una alimentacion basada en la dieta mediterranea: aceite de oliva, pescado, legumbres, frutas y verduras variadas.
- Mantén la actividad fisica regular: al menos 150 minutos semanales de ejercicio moderado.
- Asegura un buen descanso: 7-8 horas de sueno reparador.
- Hidratacion adecuada: 1.5-2 litros de agua al dia.
- Realiza controles analiticos anuales de seguimiento.
- Modera el consumo de alcohol y evita el tabaco.

¡Enhorabuena por tus resultados!""",

    """Excelentes resultados. Todos los marcadores estan en rango y no se detectan alteraciones.

Para mantener esta buena salud:
- Continua con tus habitos alimentarios actuales, priorizando alimentos frescos y de temporada.
- El ejercicio regular es la mejor inversion en salud a largo plazo: sigue activo/a.
- Gestiona el estres: es un factor silencioso que afecta a muchos parametros.
- Duerme bien y mantén horarios regulares.
- Proximo control analitico recomendado: en 12 meses.""",

    """Los resultados de tu analitica son normales. No se observan valores fuera de rango que requieran intervencion.

Consejos generales de salud:
- Alimentacion variada y equilibrada, rica en fibra, omega-3 y antioxidantes.
- Actividad fisica diaria: caminar, nadar, bicicleta, lo que disfrutes.
- Mantén un peso estable y saludable.
- Limita ultraprocesados, azucares anadidos y grasas saturadas.
- Hidratate bien a lo largo del dia.
- Proxima revision analitica: en 1 ano si no hay sintomas nuevos.""",
]

# ============================================================
# INTRO PHRASES - Varied opening lines
# ============================================================
INTROS_ABNORMAL = [
    "Analizando tus resultados, hay algunos valores que merecen atencion:",
    "Tras revisar tu analitica, identifico los siguientes puntos importantes:",
    "Estos son los hallazgos mas relevantes de tu analitica de sangre:",
    "A continuacion te detallo los valores alterados y mis recomendaciones:",
    "He revisado tus resultados y te comento lo que he encontrado:",
]

CLOSINGS = [
    "\n\nRecuerda que estas recomendaciones son orientativas. Consulta siempre con tu medico antes de realizar cambios significativos en tu dieta o estilo de vida.",
    "\n\nEstas indicaciones son generales y deben complementarse con la valoracion de tu medico, que conoce tu historial completo.",
    "\n\nImportante: estas recomendaciones no sustituyen la consulta medica. Tu medico te indicara si necesitas algun tratamiento adicional o pruebas complementarias.",
    "\n\nSigue estas recomendaciones y repite la analitica en el plazo que te indique tu medico para comprobar la evolucion.",
]

# ============================================================
# GENERATION LOGIC
# ============================================================

def get_value_and_status(marker_name, sex):
    """Generate a realistic value with status (Normal, ALTO, BAJO)"""
    info = MARKERS[marker_name]

    # Determine ranges based on sex
    range_key_m = "range_m"
    range_key_f = "range_f"
    low_m = f"low_range_m" if f"low_range_m" in info else "low_range"
    low_f = f"low_range_f" if f"low_range_f" in info else "low_range"
    high_m = f"high_range_m" if f"high_range_m" in info else "high_range"
    high_f = f"high_range_f" if f"high_range_f" in info else "high_range"

    normal_range = info[range_key_m] if sex == "Hombre" else info[range_key_f]
    low_key = low_m if sex == "Hombre" else low_f
    high_key = high_m if sex == "Hombre" else high_f

    # Decide status: 55% normal, 30% abnormal, 15% borderline
    roll = random.random()
    if roll < 0.55:
        # Normal
        lo, hi = normal_range
        val = random.uniform(lo, hi)
        status = "Normal"
    elif roll < 0.85:
        # Abnormal
        if random.random() < 0.5 and low_key in info:
            lo, hi = info[low_key]
            val = random.uniform(lo, hi)
            status = "BAJO"
        elif high_key in info:
            lo, hi = info[high_key]
            val = random.uniform(lo, hi)
            status = "ALTO"
        elif low_key in info:
            lo, hi = info[low_key]
            val = random.uniform(lo, hi)
            status = "BAJO"
        else:
            lo, hi = normal_range
            val = random.uniform(lo, hi)
            status = "Normal"
    else:
        # Borderline - slightly out
        lo, hi = normal_range
        if random.random() < 0.5:
            val = lo * random.uniform(0.92, 0.99)
            status = "BAJO" if low_key in info else "Normal"
        else:
            val = hi * random.uniform(1.01, 1.08)
            status = "ALTO" if high_key in info else "Normal"

    # Format value
    unit = info["unit"]
    if unit in ("/uL",) and val > 1000:
        val = round(val)
    elif unit in ("mg/dL", "ug/dL", "ng/mL", "pg/mL", "U/L"):
        val = round(val, 1) if val < 100 else round(val)
    elif unit in ("g/dL", "mUI/L"):
        val = round(val, 1)
    elif unit == "%":
        val = round(val, 1)
    else:
        val = round(val, 1)

    ref_lo, ref_hi = normal_range
    ref_str = f"{ref_lo}-{ref_hi}"

    return val, status, unit, ref_str


def apply_correlations(markers_data):
    """Apply realistic medical correlations"""
    marker_dict = {m["name"]: m for m in markers_data}

    # High glucose -> often high triglycerides
    if "Glucosa" in marker_dict and marker_dict["Glucosa"]["status"] == "ALTO":
        if "Trigliceridos" in marker_dict and marker_dict["Trigliceridos"]["status"] == "Normal":
            if random.random() < 0.4:
                marker_dict["Trigliceridos"]["status"] = "ALTO"
                marker_dict["Trigliceridos"]["value"] = random.uniform(155, 280)

    # Low hemoglobin -> often low hematocrit, low iron, low ferritin
    if "Hemoglobina" in marker_dict and marker_dict["Hemoglobina"]["status"] == "BAJO":
        for related in ["Hematocrito", "Hierro serico", "Ferritina"]:
            if related in marker_dict and marker_dict[related]["status"] == "Normal":
                if random.random() < 0.5:
                    marker_dict[related]["status"] = "BAJO"

    # High ALT -> often high AST and GGT
    if "ALT (GPT)" in marker_dict and marker_dict["ALT (GPT)"]["status"] == "ALTO":
        for related in ["AST (GOT)", "GGT"]:
            if related in marker_dict and marker_dict[related]["status"] == "Normal":
                if random.random() < 0.45:
                    marker_dict[related]["status"] = "ALTO"

    # High LDL -> often high total cholesterol
    if "LDL" in marker_dict and marker_dict["LDL"]["status"] == "ALTO":
        if "Colesterol Total" in marker_dict and marker_dict["Colesterol Total"]["status"] == "Normal":
            if random.random() < 0.5:
                marker_dict["Colesterol Total"]["status"] = "ALTO"

    return markers_data


def build_recommendation(markers_data):
    """Build a natural, detailed recommendation based on abnormal values"""
    abnormal = [m for m in markers_data if m["status"] != "Normal"]

    if not abnormal:
        return random.choice(NORMAL_RESPONSES)

    parts = [random.choice(INTROS_ABNORMAL), ""]

    for m in abnormal:
        key = f"{m['name']}_{m['status'].lower().replace('alto','high').replace('bajo','low')}"
        if key in RECOMMENDATIONS:
            recs = RECOMMENDATIONS[key]
            parts.append(f"**{m['name']}** ({m['value']} {m['unit']}) - {m['status']}:")
            parts.append(random.choice(recs))
            parts.append("")

    parts.append(random.choice(CLOSINGS))

    return "\n".join(parts)


def generate_sample():
    """Generate one training sample"""
    sex = random.choice(["Hombre", "Mujer"])
    age = random.randint(18, 80)

    # Pick 4-8 markers
    num_markers = random.randint(4, 8)
    selected = random.sample(list(MARKERS.keys()), num_markers)

    markers_data = []
    for name in selected:
        val, status, unit, ref_str = get_value_and_status(name, sex)
        markers_data.append({
            "name": name,
            "value": val,
            "status": status,
            "unit": unit,
            "ref": ref_str,
        })

    markers_data = apply_correlations(markers_data)

    # Build input
    lines = [f"Paciente: {sex}, {age} anos.", "Resultados de analitica de sangre:", ""]
    for m in markers_data:
        lines.append(f"- {m['name']}: {m['value']} {m['unit']} [{m['status']}] (ref: {m['ref']})")

    input_text = "\n".join(lines)
    output_text = build_recommendation(markers_data)

    return {
        "input": input_text,
        "output": output_text,
        "markers": [m["name"] for m in markers_data],
    }


def main():
    os.makedirs(os.path.join(DATA_DIR), exist_ok=True)

    print("Generating v2 dataset (knowledge-distilled)...")

    # Training set
    train_samples = []
    for i in range(3000):
        train_samples.append(generate_sample())

    train_path = os.path.join(DATA_DIR, "train_v2.jsonl")
    with open(train_path, "w") as f:
        for s in train_samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"  Training: {len(train_samples)} samples -> {train_path}")

    # Test set (different seed)
    random.seed(99)
    test_samples = []
    for i in range(200):
        test_samples.append(generate_sample())

    test_path = os.path.join(DATA_DIR, "test_v2.jsonl")
    with open(test_path, "w") as f:
        for s in test_samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"  Test: {len(test_samples)} samples -> {test_path}")

    # Stats
    abnormal_count = sum(1 for s in train_samples if "ALTO" in s["input"] or "BAJO" in s["input"])
    print(f"\n  Samples with abnormal values: {abnormal_count}/{len(train_samples)} ({abnormal_count*100//len(train_samples)}%)")

    # Preview
    print("\n--- Sample preview ---")
    sample = next(s for s in train_samples if "ALTO" in s["input"])
    print(sample["input"][:300])
    print("...")
    print(sample["output"][:300])
    print("...")

    print("\nDone!")


if __name__ == "__main__":
    main()
