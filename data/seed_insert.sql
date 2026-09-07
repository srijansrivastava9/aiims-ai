-- Seed insert script for Supabase SQL Editor
-- Run this in Supabase -> SQL Editor to bypass RLS
-- Safe to re-run (uses ON CONFLICT / WHERE NOT EXISTS)

-- MedDRA terms
INSERT INTO meddra_terms (term, code)
VALUES
  ('Headache', 'M001'), ('Nausea', 'M002'), ('Vomiting', 'M003'),
  ('Diarrhoea', 'M004'), ('Dizziness', 'M005'), ('Fatigue', 'M006'),
  ('Rash', 'M007'), ('Pruritus', 'M008'), ('Urticaria', 'M009'),
  ('Abdominal pain', 'M010'), ('Constipation', 'M011'), ('Dyspepsia', 'M012'),
  ('Chest pain', 'M013'), ('Dyspnoea', 'M014'), ('Palpitations', 'M015'),
  ('Hypertension', 'M016'), ('Hypotension', 'M017'), ('Tachycardia', 'M018'),
  ('Bradycardia', 'M019'), ('Fever', 'M020'), ('Chills', 'M021'),
  ('Myalgia', 'M022'), ('Arthralgia', 'M023'), ('Back pain', 'M024'),
  ('Insomnia', 'M025'), ('Somnolence', 'M026'), ('Anxiety', 'M027'),
  ('Depression', 'M028'), ('Confusion', 'M029'), ('Tremor', 'M030'),
  ('Seizure', 'M031'), ('Syncope', 'M032'), ('Blurred vision', 'M033'),
  ('Tinnitus', 'M034'), ('Epistaxis', 'M035'), ('Cough', 'M036'),
  ('Pharyngitis', 'M037'), ('Rhinitis', 'M038'), ('Sinusitis', 'M039'),
  ('Bronchitis', 'M040'), ('Pneumonia', 'M041'), ('Urinary tract infection', 'M042'),
  ('Dysuria', 'M043'), ('Haematuria', 'M044'), ('Oedema peripheral', 'M045'),
  ('Weight decreased', 'M046'), ('Weight increased', 'M047'), ('Anorexia', 'M048'),
  ('Hyperglycaemia', 'M049'), ('Hypoglycaemia', 'M050'), ('Hyperkalaemia', 'M051'),
  ('Hypokalaemia', 'M052'), ('Anaemia', 'M053'), ('Leukopenia', 'M054'),
  ('Thrombocytopenia', 'M055'), ('Elevated ALT', 'M056'), ('Elevated AST', 'M057'),
  ('Elevated bilirubin', 'M058'), ('Jaundice', 'M059'), ('Hepatotoxicity', 'M060'),
  ('Acute kidney injury', 'M061'), ('Proteinuria', 'M062'), ('Renal impairment', 'M063'),
  ('Injection site reaction', 'M064'), ('Infusion related reaction', 'M065'),
  ('Anaphylaxis', 'M066'), ('Angioedema', 'M067'), ('Stevens-Johnson syndrome', 'M068'),
  ('Toxic epidermal necrolysis', 'M069'), ('Rhabdomyolysis', 'M070'),
  ('QT prolongation', 'M071'), ('Torsade de pointes', 'M072'),
  ('Gastrointestinal bleeding', 'M073'), ('Pancreatitis', 'M074'),
  ('Agranulocytosis', 'M075')
ON CONFLICT (code) DO NOTHING;

-- Guideline chunks
INSERT INTO guideline_chunks (source, content)
SELECT * FROM (VALUES
  ('GCP', 'Investigators must maintain accurate case histories and record all observations.'),
  ('GCP', 'Informed consent must be obtained before any trial-related procedures.'),
  ('GCP', 'Source data must be attributable, legible, contemporaneous, original, and accurate.'),
  ('GCP', 'The sponsor is responsible for implementing and maintaining quality assurance systems.'),
  ('GCP', 'All adverse events must be reported to the sponsor and ethics committee promptly.'),
  ('GCP', 'Trial monitoring should verify that the trial is conducted according to the protocol.'),
  ('GCP', 'Data integrity must be ensured through validation and audit trails.'),
  ('GCP', 'The investigator must have adequate resources to conduct the trial properly.'),
  ('Ayush SOP', 'Ayurvedic trial drugs must be prepared according to classical texts or approved formulations.'),
  ('Ayush SOP', 'Quality control of herbal raw materials must include identification and standardization.'),
  ('Ayush SOP', 'Panchakarma procedures require trained therapists and documented consent.'),
  ('Ayush SOP', 'Dietary restrictions during Ayurvedic trials must be recorded in the case report form.'),
  ('Ayush SOP', 'Prakriti assessment should be done using standardized questionnaires before enrollment.'),
  ('Ayush SOP', 'Herbo-mineral formulations must be tested for heavy metals before administration.'),
  ('Ayush SOP', 'Shamana and Shodhana therapies have different monitoring requirements during trials.'),
  ('Ayush SOP', 'Integration of Ayurveda with modern diagnostics requires protocol-defined endpoints.'),
  ('Ethics', 'Ethics Committee approval must be obtained before trial initiation. [DEMO PLACEHOLDER: renewal every 1 year]'),
  ('Ethics', 'Continuing review of ongoing trials is mandatory for EC-approved studies. [DEMO PLACEHOLDER: annual renewal]'),
  ('Ethics', 'Vulnerable populations require additional safeguards and enhanced consent procedures.'),
  ('Ethics', 'The EC must review all protocol amendments before implementation.'),
  ('Ethics', 'Participant compensation and insurance must be clearly defined in the protocol.'),
  ('Ethics', 'Data safety monitoring boards may be required for high-risk trials.'),
  ('Ethics', 'Emergency use of investigational drugs requires expedited EC review.'),
  ('Ethics', 'Trial termination must be reported to the EC within 15 days.'),
  ('Pharmacovigilance', 'Serious adverse events must be reported within 24 hours. [DEMO PLACEHOLDER: 24h SAE deadline]'),
  ('Pharmacovigilance', 'Non-serious adverse events must be reported within 15 days. [DEMO PLACEHOLDER: 15d AE deadline]'),
  ('Pharmacovigilance', 'All suspected unexpected serious adverse reactions must be documented and analyzed.'),
  ('Pharmacovigilance', 'The sponsor must maintain a safety database for all trial-related adverse events.'),
  ('Pharmacovigilance', 'Periodic safety update reports are required for long-term trials.'),
  ('Pharmacovigilance', 'Causality assessment should follow WHO-UMC or other standardized methods.'),
  ('Pharmacovigilance', 'Signal detection requires systematic review of accumulated safety data.'),
  ('Pharmacovigilance', 'Risk management plans must be updated based on emerging safety data.'),
  ('CTRI', 'All clinical trials in India must be registered in CTRI before enrollment of the first participant.'),
  ('CTRI', 'Trial registration must include the full protocol and primary/secondary outcomes.'),
  ('CTRI', 'Results of completed trials must be posted in CTRI within 12 months of completion.'),
  ('CTRI', 'Any changes to the registered trial details must be updated in CTRI promptly.'),
  ('CTRI', 'CTRI registration number must be cited in all publications arising from the trial.'),
  ('CTRI', 'Phase I trials for Ayurveda drugs require specific safety endpoints in CTRI.'),
  ('CTRI', 'Multi-center trials must list all participating sites in the CTRI registration.'),
  ('CTRI', 'Post-trial access to investigational drugs must be declared in CTRI.')
) AS v(source, content)
WHERE NOT EXISTS (
  SELECT 1 FROM guideline_chunks g
  WHERE g.source = v.source AND g.content = v.content
);
