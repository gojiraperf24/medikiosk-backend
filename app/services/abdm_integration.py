"""ABDM (Ayushman Bharat Digital Mission) integration service"""
from typing import Dict, Any, Optional
import httpx
import json
from datetime import datetime
from app.core.config import get_settings
from app.utils.logger import setup_logger
from app.utils.fhir_converter import FHIRConverter, convert_to_fhir_bundle

logger = setup_logger(__name__)
settings = get_settings()


class ABDMIntegration:
    """Integration with ABDM ecosystem for health data exchange"""
    
    def __init__(self):
        """Initialize ABDM integration"""
        self.client_id = settings.ABDM_CLIENT_ID
        self.client_secret = settings.ABDM_CLIENT_SECRET
        self.base_url = settings.ABDM_BASE_URL
        self.gateway_url = settings.ABDM_GATEWAY_URL
        self.access_token = None
        self.fhir_converter = FHIRConverter()
    
    async def authenticate(self) -> bool:
        """Authenticate with ABDM gateway using client credentials"""
        logger.info("Authenticating with ABDM gateway")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.gateway_url}/oauth2/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get("access_token")
                    logger.info("ABDM authentication successful")
                    return True
                else:
                    logger.error(f"ABDM authentication failed: {response.text}")
                    return False
        
        except Exception as e:
            logger.error(f"ABDM authentication error: {str(e)}")
            return False
    
    async def link_abha_id(
        self,
        patient_id: str,
        abha_id: str,
        abha_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Link patient's ABHA ID for health record access
        
        Args:
            patient_id: MediKiosk patient ID
            abha_id: ABHA ID or Aadhaar number
            abha_address: ABHA address (username@abdm)
        """
        logger.info(f"Linking ABHA ID for patient: {patient_id}")
        
        try:
            if not self.access_token:
                auth_success = await self.authenticate()
                if not auth_success:
                    return {"status": "failed", "error": "ABDM authentication failed"}
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "healthId": abha_id,
                    "healthIdType": "ABHA_ID" if len(abha_id) == 12 else "AADHAR"
                }
                
                if abha_address:
                    payload["abhaAddress"] = abha_address
                
                response = await client.post(
                    f"{self.gateway_url}/v0.5/accounts/link",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    logger.info(f"ABHA ID linked successfully for patient: {patient_id}")
                    return {
                        "status": "success",
                        "patient_id": patient_id,
                        "abha_id": abha_id,
                        "linked_at": datetime.utcnow().isoformat()
                    }
                else:
                    logger.error(f"ABHA linking failed: {response.text}")
                    return {"status": "failed", "error": response.text}
        
        except Exception as e:
            logger.error(f"ABHA linking error: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def push_clinical_summary(
        self,
        patient_id: str,
        abha_id: str,
        summary_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Push clinical summary to patient's ABDM personal health record
        
        Converts summary to FHIR format and sends to HIE
        """
        logger.info(f"Pushing clinical summary to ABDM for patient: {patient_id}")
        
        try:
            if not self.access_token:
                auth_success = await self.authenticate()
                if not auth_success:
                    return {"status": "failed", "error": "ABDM authentication failed"}
            
            # Convert summary to FHIR
            fhir_summary = self.fhir_converter.summary_to_fhir(
                summary_data,
                patient_id
            )
            
            # Create FHIR bundle
            bundle = convert_to_fhir_bundle([fhir_summary])
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/fhir+json"
                }
                
                response = await client.post(
                    f"{self.gateway_url}/v0.5/health-information/hiu/on-request",
                    json=bundle,
                    headers=headers
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Summary pushed successfully to ABDM for patient: {patient_id}")
                    return {
                        "status": "success",
                        "patient_id": patient_id,
                        "pushed_at": datetime.utcnow().isoformat()
                    }
                else:
                    logger.error(f"ABDM push failed: {response.text}")
                    return {"status": "failed", "error": response.text}
        
        except Exception as e:
            logger.error(f"ABDM push error: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def fetch_abha_records(
        self,
        patient_id: str,
        abha_id: str
    ) -> Dict[str, Any]:
        """Fetch patient's existing health records from ABDM gateway"""
        logger.info(f"Fetching ABDM records for patient: {patient_id}")
        
        try:
            if not self.access_token:
                auth_success = await self.authenticate()
                if not auth_success:
                    return {"status": "failed", "error": "ABDM authentication failed"}
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                
                response = await client.get(
                    f"{self.gateway_url}/v0.5/records/@{abha_id}/documents",
                    headers=headers
                )
                
                if response.status_code == 200:
                    records = response.json()
                    logger.info(f"Successfully fetched {len(records)} records from ABDM")
                    return {
                        "status": "success",
                        "records": records
                    }
                else:
                    logger.error(f"ABDM fetch failed: {response.text}")
                    return {"status": "failed", "error": response.text}
        
        except Exception as e:
            logger.error(f"ABDM fetch error: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def check_consent_status(
        self,
        patient_id: str,
        abha_id: str
    ) -> Dict[str, Any]:
        """Check patient's data sharing consent status with ABDM"""
        logger.info(f"Checking consent status for patient: {patient_id}")
        
        try:
            if not self.access_token:
                auth_success = await self.authenticate()
                if not auth_success:
                    return {"status": "failed", "error": "ABDM authentication failed"}
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                
                response = await client.get(
                    f"{self.gateway_url}/v0.5/consents/user/@{abha_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    consent_data = response.json()
                    return {
                        "status": "success",
                        "consent_status": consent_data
                    }
                else:
                    return {"status": "failed", "error": response.text}
        
        except Exception as e:
            logger.error(f"Consent check error: {str(e)}")
            return {"status": "failed", "error": str(e)}
