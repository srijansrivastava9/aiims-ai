"""Generate synthetic MedDRA-style terms and guideline chunks."""
import json
import uuid
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from config import DATA_DIR


def generate_meddra_terms():
    """Generate 75 synthetic MedDRA-style preferred terms."""
    terms = [
        ("M001", "Headache"), ("M002", "Nausea"), ("M003", "Vomiting"),
        ("M004", "Diarrhoea"), ("M005", "Dizziness"), ("M006", "Fatigue"),
        ("M007", "Rash"), ("M008", "Pruritus"), ("M009", "Urticaria"),
        ("M010", "Abdominal pain"), ("M011", "Constipation"), ("M012", "Dyspepsia"),
        ("M013", "Chest pain"), ("M014", "Dyspnoea"), ("M015", "Palpitations"),
        ("M016", "Hypertension"), ("M017", "Hypotension"), ("M018", "Tachycardia"),
        ("M019", "Bradycardia"), ("M020", "Fever"), ("M021", "Chills"),
        ("M022", "Myalgia"), ("M023", "Arthralgia"), ("M024", "Back pain"),
        ("M025", "Insomnia"), ("M026", "Somnolence"), ("M027", "Anxiety"),
        ("M028", "Depression"), ("M029", "Confusion"), ("M030", "Tremor"),
        ("M031", "Seizure"), ("M032", "Syncope"), ("M033", "Blurred vision"),
        ("M034", "Tinnitus"), ("M035", "Epistaxis"), ("M036", "Cough"),
        ("M037", "Pharyngitis"), ("M038", "Rhinitis"), ("M039", "Sinusitis"),
        ("M040", "Bronchitis"), ("M041", "Pneumonia"), ("M042", "Urinary tract infection"),
        ("M043", "Dysuria"), ("M044", "Haematuria"), ("M045", "Oedema peripheral"),
        ("M046", "Weight decreased"), ("M047", "Weight increased"), ("M048", "Anorexia"),
        ("M049", "Hyperglycaemia"), ("M050", "Hypoglycaemia"), ("M051", "Hyperkalaemia"),
        ("M052", "Hypokalaemia"), ("M053", "Anaemia"), ("M054", "Leukopenia"),
        ("M055", "Thrombocytopenia"), ("M056", "Elevated ALT"), ("M057", "Elevated AST"),
        ("M058", "Elevated bilirubin"), ("M059", "Jaundice"), ("M060", "Hepatotoxicity"),
        ("M061", "Acute kidney injury"), ("M062", "Proteinuria"), ("M063", "Renal impairment"),
        ("M064", "Injection site reaction"), ("M065", "Infusion related reaction"),
        ("M066", "Anaphylaxis"), ("M067", "Angioedema"), ("M068", "Stevens-Johnson syndrome"),
        ("M069", "Toxic epidermal necrolysis"), ("M070", "Rhabdomyolysis"),
        ("M071", "QT prolongation"), ("M072", "Torsade de pointes"),
        ("M073", "Gastrointestinal bleeding"), ("M074", "Pancreatitis"),
        ("M075", "Agranulocytosis"),
    ]
    return [{"term": t[1], "code": t[0]} for t in terms]


def generate_guideline_chunks():
    """Generate 40 synthetic guideline chunks across 5 sources."""
    sources = {
        "GCP": [
            "Investigators must maintain accurate case histories and record all observations.",
            "Informed consent must be obtained before any trial-related procedures.",
            "Source data must be attributable, legible, contemporaneous, original, and accurate.",
            "The sponsor is responsible for implementing and maintaining quality assurance systems.",
            "All adverse events must be reported to the sponsor and ethics committee promptly.",
            "Trial monitoring should verify that the trial is conducted according to the protocol.",
            "Data integrity must be ensured through validation and audit trails.",
            "The investigator must have adequate resources to conduct the trial properly.",
        ],
        "Ayush SOP": [
            "Ayurvedic trial drugs must be prepared according to classical texts or approved formulations.",
            "Quality control of herbal raw materials must include identification and standardization.",
            "Panchakarma procedures require trained therapists and documented consent.",
            "Dietary restrictions during Ayurvedic trials must be recorded in the case report form.",
            "Prakriti assessment should be done using standardized questionnaires before enrollment.",
            "Herbo-mineral formulations must be tested for heavy metals before administration.",
            "Shamana and Shodhana therapies have different monitoring requirements during trials.",
            "Integration of Ayurveda with modern diagnostics requires protocol-defined endpoints.",
        ],
        "Ethics": [
            "Ethics Committee approval must be obtained before trial initiation. [DEMO PLACEHOLDER: renewal every 1 year]",
            "Continuing review of ongoing trials is mandatory for EC-approved studies. [DEMO PLACEHOLDER: annual renewal]",
            "Vulnerable populations require additional safeguards and enhanced consent procedures.",
            "The EC must review all protocol amendments before implementation.",
            "Participant compensation and insurance must be clearly defined in the protocol.",
            "Data safety monitoring boards may be required for high-risk trials.",
            "Emergency use of investigational drugs requires expedited EC review.",
            "Trial termination must be reported to the EC within 15 days.",
        ],
        "Pharmacovigilance": [
            "Serious adverse events must be reported within 24 hours. [DEMO PLACEHOLDER: 24h SAE deadline]",
            "Non-serious adverse events must be reported within 15 days. [DEMO PLACEHOLDER: 15d AE deadline]",
            "All suspected unexpected serious adverse reactions must be documented and analyzed.",
            "The sponsor must maintain a safety database for all trial-related adverse events.",
            "Periodic safety update reports are required for long-term trials.",
            "Causality assessment should follow WHO-UMC or other standardized methods.",
            "Signal detection requires systematic review of accumulated safety data.",
            "Risk management plans must be updated based on emerging safety data.",
        ],
        "CTRI": [
            "All clinical trials in India must be registered in CTRI before enrollment of the first participant.",
            "Trial registration must include the full protocol and primary/secondary outcomes.",
            "Results of completed trials must be posted in CTRI within 12 months of completion.",
            "Any changes to the registered trial details must be updated in CTRI promptly.",
            "CTRI registration number must be cited in all publications arising from the trial.",
            "Phase I trials for Ayurveda drugs require specific safety endpoints in CTRI.",
            "Multi-center trials must list all participating sites in the CTRI registration.",
            "Post-trial access to investigational drugs must be declared in CTRI.",
        ],
    }
    chunks = []
    for source, contents in sources.items():
        for content in contents:
            chunks.append({"source": source, "content": content})
    return chunks


def main():
    meddra = generate_meddra_terms()
    guidelines = generate_guideline_chunks()

    (DATA_DIR / "seed_meddra_terms.json").write_text(
        json.dumps(meddra, indent=2), encoding="utf-8"
    )
    (DATA_DIR / "seed_guideline_chunks.json").write_text(
        json.dumps(guidelines, indent=2), encoding="utf-8"
    )
    print(f"Wrote {len(meddra)} meddra terms, {len(guidelines)} guideline chunks to data/")


if __name__ == "__main__":
    main()
