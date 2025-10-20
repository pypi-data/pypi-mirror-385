use helios_fhir::r4::{DetectedIssue, DetectedIssueIdentified};
use helios_fhirpath_support::IntoEvaluationResult;

#[test]
fn test_datetime_type_info() {
    // Create a DetectedIssue with identifiedDateTime
    let mut di = DetectedIssue::default();
    di.id = Some(helios_fhir::r4::Id {
        value: Some("di2".to_string()),
        id: None,
        extension: None,
    });
    di.status = helios_fhir::r4::Code {
        value: Some("final".to_string()),
        id: None,
        extension: None,
    };

    // Create a DateTime value
    let datetime = helios_fhir::r4::DateTime {
        value: Some(helios_fhir::PrecisionDateTime::parse("2016-11-12").unwrap()),
        id: None,
        extension: None,
    };

    di.identified = Some(DetectedIssueIdentified::DateTime(datetime));

    // Convert to evaluation result
    let eval_result = di.to_evaluation_result();

    // Print the structure
    println!("Full evaluation result: {:?}", eval_result);

    if let helios_fhirpath_support::EvaluationResult::Object { map, .. } = &eval_result {
        if let Some(identified) = map.get("identified") {
            println!("\nIdentified field: {:?}", identified);

            if let helios_fhirpath_support::EvaluationResult::Object { map: inner_map, .. } =
                identified
            {
                if let Some(identified_datetime) = inner_map.get("identifiedDateTime") {
                    println!("\nIdentifiedDateTime field: {:?}", identified_datetime);
                }
            }
        }
        // Also check direct access
        if let Some(identified_datetime) = map.get("identifiedDateTime") {
            println!(
                "\nDirect identifiedDateTime field: {:?}",
                identified_datetime
            );
        }
    }
}
