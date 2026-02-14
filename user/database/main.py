# user/database/main.py

from user.database.connection import DatabaseConnection


class DatabaseManager:

    def __init__(self):
        # ✅ Single shared database
        self.db = DatabaseConnection("taakra_db")

    def build_database_context(self, user_uuid: str):

        if not user_uuid:
            raise ValueError("UUID is required")

        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # 🔥 Fetch ONLY this user
            cursor.execute("""
                SELECT user_id, full_name, email, university, created_at
                FROM users
                WHERE user_id = ?
            """, (user_uuid,))
            user_row = cursor.fetchone()

            if not user_row:
                return {
                    "user": None,
                    "registrations": []
                }

            user_data = {
                "user_id": str(user_row[0]),
                "full_name": user_row[1],
                "email": user_row[2],
                "university": user_row[3],
                "created_at": str(user_row[4])
            }

            # 🔥 Fetch this user's registrations only
            cursor.execute("""
                SELECT registration_id,
                       competition_id,
                       team_name,
                       status,
                       registered_at,
                       reviewed_at,
                       reviewed_by
                FROM registrations
                WHERE user_id = ?
            """, (user_uuid,))

            rows = cursor.fetchall()

            registrations = []
            for row in rows:
                registrations.append({
                    "registration_id": row[0],
                    "competition_id": row[1],
                    "team_name": row[2],
                    "status": row[3],
                    "registered_at": str(row[4]),
                    "reviewed_at": str(row[5]) if row[5] else None,
                    "reviewed_by": str(row[6]) if row[6] else None
                })

        finally:
            cursor.close()
            conn.close()

        return {
            "user": user_data,
            "registrations": registrations
        }