"""Print the recommended SkyGuard AI judge demonstration runbook."""
SCENES = [
    ("1", "Normal streaming", "python -m simulator.stream"),
    ("2", "Isolated temperature fault", "python -m simulator.stream --scenario isolated_temperature_fault"),
    ("3", "Regional weather event", "python -m simulator.stream --scenario regional_event"),
    ("4", "Frozen sensor", "python -m simulator.stream --scenario frozen_sensor"),
    ("5", "Communication gap", "python -m simulator.stream --scenario communication_gap"),
]
for n, title, command in SCENES:
    print(f"{n}. {title}\n   {command}\n")
print("In the dashboard, select the affected station and show the Explainable AI panel:")
print("  - confidence")
print("  - SHAP feature contribution")
print("  - temporal/spatial evidence")
print("  - root-cause diagnosis")
print("  - recommended action")
print("  - AI-assisted corrected value")
