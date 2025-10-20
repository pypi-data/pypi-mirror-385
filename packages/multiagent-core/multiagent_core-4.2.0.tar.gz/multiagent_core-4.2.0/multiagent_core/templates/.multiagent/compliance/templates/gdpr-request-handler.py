"""
GDPR Request Handler
Purpose: Implement GDPR rights (Access, Erasure, Portability, Rectification)
Compliance: GDPR Articles 15, 17, 20, 16
"""

from flask import Flask, request, jsonify, send_file
from typing import Dict, List, Any
import json
import csv
import io
from datetime import datetime
import psycopg2
import redis


app = Flask(__name__)


class GDPRRequestHandler:
    """
    Handler for GDPR data subject requests.

    Implements:
    - Right to Access (Article 15)
    - Right to Erasure (Article 17)
    - Right to Portability (Article 20)
    - Right to Rectification (Article 16)
    """

    def __init__(self, db_config: Dict, redis_config: Dict):
        self.db_config = db_config
        self.redis_client = redis.Redis(**redis_config)

        # Audit log
        self.audit_log = []

    def _log_request(self, request_type: str, user_id: str, metadata: Dict = None):
        """Log GDPR request for audit trail."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_type": request_type,
            "user_id": user_id,
            "metadata": metadata or {},
        }
        self.audit_log.append(log_entry)

        # Store in database for long-term audit
        # TODO: Store in audit_logs table

    def _get_db_connection(self):
        """Get database connection."""
        return psycopg2.connect(**self.db_config)

    def handle_access_request(self, user_id: str) -> Dict[str, Any]:
        """
        GDPR Article 15: Right to Access
        Return all personal data stored about the user.
        """
        self._log_request("access", user_id)

        user_data = {
            "user_id": user_id,
            "request_date": datetime.utcnow().isoformat(),
            "data": {},
        }

        conn = self._get_db_connection()
        cursor = conn.cursor()

        # Define tables containing user data
        tables = [
            "users",
            "user_profiles",
            "user_preferences",
            "user_sessions",
            "orders",
            "payments",
            "user_activity_logs",
        ]

        for table in tables:
            try:
                cursor.execute(
                    f"SELECT * FROM {table} WHERE user_id = %s",
                    (user_id,)
                )
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                user_data["data"][table] = [
                    dict(zip(columns, row)) for row in rows
                ]
            except Exception as e:
                user_data["data"][table] = {"error": str(e)}

        # Check Redis cache for user data
        redis_keys = self.redis_client.keys(f"user:{user_id}:*")
        user_data["data"]["cache"] = {
            key.decode(): self.redis_client.get(key).decode()
            for key in redis_keys
        }

        cursor.close()
        conn.close()

        return user_data

    def handle_erasure_request(self, user_id: str, reason: str = "") -> Dict[str, Any]:
        """
        GDPR Article 17: Right to Erasure (Right to be Forgotten)
        Delete or anonymize all personal data.
        """
        self._log_request("erasure", user_id, {"reason": reason})

        deleted_records = {
            "user_id": user_id,
            "deletion_date": datetime.utcnow().isoformat(),
            "deleted_from": [],
        }

        conn = self._get_db_connection()
        cursor = conn.cursor()

        # Tables to delete user data from
        deletion_tables = [
            "user_sessions",
            "user_activity_logs",
            "user_preferences",
        ]

        # Tables to anonymize (retain for legal/financial compliance)
        anonymization_tables = [
            "orders",
            "payments",
        ]

        # Delete from deletion tables
        for table in deletion_tables:
            try:
                cursor.execute(
                    f"DELETE FROM {table} WHERE user_id = %s",
                    (user_id,)
                )
                deleted_records["deleted_from"].append(table)
            except Exception as e:
                deleted_records["deleted_from"].append({
                    "table": table,
                    "error": str(e)
                })

        # Anonymize in anonymization tables
        for table in anonymization_tables:
            try:
                cursor.execute(
                    f"""UPDATE {table}
                        SET user_id = 'ANONYMIZED',
                            email = 'anonymized@example.com',
                            name = 'ANONYMIZED USER'
                        WHERE user_id = %s""",
                    (user_id,)
                )
                deleted_records["deleted_from"].append(f"{table} (anonymized)")
            except Exception as e:
                deleted_records["deleted_from"].append({
                    "table": f"{table} (anonymization failed)",
                    "error": str(e)
                })

        # Finally, anonymize the user profile
        try:
            cursor.execute(
                """UPDATE users
                   SET email = %s,
                       name = 'ANONYMIZED USER',
                       phone = NULL,
                       address = NULL,
                       deleted_at = NOW()
                   WHERE user_id = %s""",
                (f"anonymized_{user_id}@example.com", user_id)
            )
            deleted_records["deleted_from"].append("users (anonymized)")
        except Exception as e:
            deleted_records["deleted_from"].append({
                "table": "users",
                "error": str(e)
            })

        # Delete from Redis cache
        redis_keys = self.redis_client.keys(f"user:{user_id}:*")
        if redis_keys:
            self.redis_client.delete(*redis_keys)
            deleted_records["deleted_from"].append("redis_cache")

        conn.commit()
        cursor.close()
        conn.close()

        return deleted_records

    def handle_portability_request(self, user_id: str, format: str = "json") -> Any:
        """
        GDPR Article 20: Right to Data Portability
        Export user data in machine-readable format (JSON, CSV, XML).
        """
        self._log_request("portability", user_id, {"format": format})

        # Get all user data
        user_data = self.handle_access_request(user_id)

        if format == "json":
            return json.dumps(user_data, indent=2, default=str)
        elif format == "csv":
            return self._export_to_csv(user_data)
        elif format == "xml":
            return self._export_to_xml(user_data)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_to_csv(self, user_data: Dict) -> str:
        """Export user data to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Table", "Field", "Value"])

        # Write data
        for table, records in user_data["data"].items():
            if isinstance(records, list):
                for record in records:
                    for field, value in record.items():
                        writer.writerow([table, field, value])

        return output.getvalue()

    def _export_to_xml(self, user_data: Dict) -> str:
        """Export user data to XML format."""
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<user_data>\n'

        for table, records in user_data["data"].items():
            xml += f"  <{table}>\n"
            if isinstance(records, list):
                for record in records:
                    xml += "    <record>\n"
                    for field, value in record.items():
                        xml += f"      <{field}>{value}</{field}>\n"
                    xml += "    </record>\n"
            xml += f"  </{table}>\n"

        xml += "</user_data>"
        return xml

    def handle_rectification_request(
        self, user_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        GDPR Article 16: Right to Rectification
        Allow user to correct inaccurate personal data.
        """
        self._log_request("rectification", user_id, {"updates": updates})

        conn = self._get_db_connection()
        cursor = conn.cursor()

        # Validate and update allowed fields
        allowed_fields = ["email", "name", "phone", "address"]
        updated_fields = []

        for field, value in updates.items():
            if field in allowed_fields:
                try:
                    cursor.execute(
                        f"UPDATE users SET {field} = %s WHERE user_id = %s",
                        (value, user_id)
                    )
                    updated_fields.append(field)
                except Exception as e:
                    updated_fields.append({
                        "field": field,
                        "error": str(e)
                    })

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "user_id": user_id,
            "update_date": datetime.utcnow().isoformat(),
            "updated_fields": updated_fields,
        }


# Flask API Endpoints
gdpr_handler = GDPRRequestHandler(
    db_config={
        "host": "localhost",
        "database": "myapp",
        "user": "user",
        "password": "password",
    },
    redis_config={
        "host": "localhost",
        "port": 6379,
        "db": 0,
    }
)


@app.route("/api/gdpr/access/<user_id>", methods=["GET"])
def gdpr_access_request(user_id: str):
    """Handle GDPR access request."""
    try:
        data = gdpr_handler.handle_access_request(user_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/gdpr/erasure/<user_id>", methods=["POST"])
def gdpr_erasure_request(user_id: str):
    """Handle GDPR erasure request."""
    try:
        reason = request.json.get("reason", "")
        data = gdpr_handler.handle_erasure_request(user_id, reason)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/gdpr/portability/<user_id>", methods=["GET"])
def gdpr_portability_request(user_id: str):
    """Handle GDPR portability request."""
    try:
        format = request.args.get("format", "json")
        data = gdpr_handler.handle_portability_request(user_id, format)

        if format == "json":
            return jsonify(json.loads(data)), 200
        elif format == "csv":
            return send_file(
                io.BytesIO(data.encode()),
                mimetype="text/csv",
                as_attachment=True,
                download_name=f"user_data_{user_id}.csv"
            )
        else:
            return data, 200, {"Content-Type": "application/xml"}
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/gdpr/rectification/<user_id>", methods=["POST"])
def gdpr_rectification_request(user_id: str):
    """Handle GDPR rectification request."""
    try:
        updates = request.json
        data = gdpr_handler.handle_rectification_request(user_id, updates)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
