use helios_fhir::r4::{Observation, ObservationEffective};
use helios_fhirpath_support::IntoEvaluationResult;

#[test]
fn test_instant_type_info() {
    // Create an observation with effectiveInstant
    let mut obs = Observation::default();
    obs.id = Some(helios_fhir::r4::Id {
        value: Some("o1".to_string()),
        id: None,
        extension: None,
    });
    obs.status = helios_fhir::r4::Code {
        value: Some("final".to_string()),
        id: None,
        extension: None,
    };

    // Create an instant value
    let instant = helios_fhir::r4::Instant {
        value: Some(helios_fhir::PrecisionInstant::parse("2015-02-07T13:28:17.239+02:00").unwrap()),
        id: None,
        extension: None,
    };

    obs.effective = Some(ObservationEffective::Instant(instant));

    // Convert to evaluation result
    let eval_result = obs.to_evaluation_result();

    // Print the structure
    println!("Full evaluation result: {:?}", eval_result);

    if let helios_fhirpath_support::EvaluationResult::Object { map, .. } = &eval_result {
        if let Some(effective) = map.get("effective") {
            println!("\nEffective field: {:?}", effective);

            if let helios_fhirpath_support::EvaluationResult::Object { map: inner_map, .. } =
                effective
            {
                if let Some(effective_instant) = inner_map.get("effectiveInstant") {
                    println!("\nEffectiveInstant field: {:?}", effective_instant);
                }
            }
        }
    }
}
