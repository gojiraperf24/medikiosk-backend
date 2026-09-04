"""FHIR conversion utilities for ABDM integration"""
from typing import Dict, Any, Optional
from datetime import datetime
import json


class FHIRConverter:
    """Convert MediKiosk data to FHIR format"""
    
    @staticmethod
    def patient_to_fhir(patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert patient data to FHIR Patient resource"""
        return {
            "resourceType": "Patient",
            "id": patient_data.get("id"),
            "identifier": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                "code": "AADHAR"
                            }
                        ]
                    },
                    "value": patient_data.get("aadhaar_number")
                } if patient_data.get("aadhaar_number") else None,
                {
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                "code": "AADHAR"
                            }
                        ]
                    },
                    "value": patient_data.get("abha_id")
                } if patient_data.get("abha_id") else None
            ],
            "name": [
                {
                    "family": patient_data.get("last_name"),
                    "given": [patient_data.get("first_name")]
                }
            ],
            "birthDate": patient_data.get("date_of_birth"),
            "gender": patient_data.get("gender", "unknown").lower(),
            "telecom": [
                {"system": "phone", "value": patient_data.get("phone")} if patient_data.get("phone") else None,
                {"system": "email", "value": patient_data.get("email")} if patient_data.get("email") else None
            ]
        }
    
    @staticmethod
    def summary_to_fhir(summary_data: Dict[str, Any], patient_id: str) -> Dict[str, Any]:
        """Convert clinical summary to FHIR DocumentReference"""
        return {
            "resourceType": "DocumentReference",
            "id": summary_data.get("id"),
            "status": "current",
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "type": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "11503-0",
                        "display": "Medical records"
                    }
                ]
            },
            "content": [
                {
                    "attachment": {
                        "contentType": "text/plain",
                        "data": summary_data.get("summary_text", "").encode('utf-8').hex()
                    }
                }
            ],
            "date": datetime.utcnow().isoformat(),
            "description": "Patient clinical history summary from MediKiosk"
        }
    
    @staticmethod
    def observation_to_fhir(
        observation_data: Dict[str, Any],
        patient_id: str,
        obs_type: str = "laboratory"
    ) -> Dict[str, Any]:
        """Convert investigation/lab value to FHIR Observation"""
        return {
            "resourceType": "Observation",
            "id": observation_data.get("id"),
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": obs_type
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": observation_data.get("code", "unknown")
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "value": observation_data.get("value"),
            "referenceRange": [
                {
                    "low": {"value": observation_data.get("reference_low")},
                    "high": {"value": observation_data.get("reference_high")}
                }
            ] if observation_data.get("reference_low") else []
        }
    
    @staticmethod
    def condition_to_fhir(diagnosis: Dict[str, Any], patient_id: str) -> Dict[str, Any]:
        """Convert diagnosis to FHIR Condition resource"""
        return {
            "resourceType": "Condition",
            "id": diagnosis.get("id"),
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "code": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": diagnosis.get("snomed_code", "unknown"),
                        "display": diagnosis.get("name")
                    }
                ]
            },
            "onsetDateTime": diagnosis.get("onset_date"),
            "abatementDateTime": diagnosis.get("resolution_date"),
            "recordedDate": datetime.utcnow().isoformat()
        }


def convert_to_fhir_bundle(
    resources: list,
    bundle_type: str = "collection"
) -> Dict[str, Any]:
    """Convert list of FHIR resources to FHIR Bundle"""
    return {
        "resourceType": "Bundle",
        "type": bundle_type,
        "entry": [
            {
                "resource": resource,
                "request": {
                    "method": "POST",
                    "url": f"{resource.get('resourceType')}"
                }
            }
            for resource in resources if resource
        ]
    }
