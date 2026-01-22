def get_request_info(token: str) -> dict:
    return {
        "apiId": "Rainmaker",
        "ver": "1.0",
        "ts": 0,
        "action": "create",
        "msgId": "1764742386562",
        "authToken": token,
        "userInfo": {
            "id": 120641,
            "userName": "SUPERUSER",
            "type": "EMPLOYEE",
            "uuid": "f7ff59df-f78f-4b98-adc4-6b0561594a62",
            "tenantId": "st",
            "roles": [
                
            {
                "name": "Studio Designer",
                "code": "STUDIO_DESIGNER",
                "tenantId": "st"
            },
            {
                "name": "Localisation admin",
                "code": "LOC_ADMIN",
                "tenantId": "st"
            },
            {
                "name": "MDMS ADMIN",
                "code": "MDMS_ADMIN",
                "tenantId": "st"
            },
            {
                "name": "STUDIO ADMIN",
                "code": "STUDIO_ADMIN",
                "tenantId": "st"
            },
            {
                "name": "HRMS Admin",
                "code": "HRMS_ADMIN",
                "tenantId": "st"
            }
        
            ]
        }
    }