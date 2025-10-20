use helios_fhir::r4::{Instant, ObservationEffective};
use helios_fhirpath_support::IntoEvaluationResult;

#[test]
fn test_enum_conversion() {
    // Create an instant value
    let instant = Instant {
        value: Some(helios_fhir::PrecisionInstant::parse("2015-02-07T13:28:17.239+02:00").unwrap()),
        id: None,
        extension: None,
    };

    // Create the enum variant
    let effective = ObservationEffective::Instant(instant);

    // Convert to evaluation result
    let eval_result = effective.to_evaluation_result();

    // Print the result
    println!("Enum conversion result: {:?}", eval_result);
}
