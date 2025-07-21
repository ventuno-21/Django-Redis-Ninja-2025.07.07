import csv
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import connection
from app_polls.models import Poll


class Command(BaseCommand):
    help = "Load polls data from CSV file"

    def handle(self, *args, **kwargs):
        csv_file_path = "/app/polls.csv"

        try:
            with open(csv_file_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    try:
                        # 🔍 Attempt to decode JSON from the 'text' column
                        text_data = json.loads(row["text"])
                    except json.JSONDecodeError as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"❌ Invalid JSON in row {row['id']}: {row['text']} - {e}"
                            )
                        )
                        continue

                    # ⚙️ Optional fields with safe defaults
                    is_active = row.get("is_active", "True").lower() == "true"
                    expire_at_raw = row.get("expire_at", "").strip()

                    # ⏰ Parse expire_at if present, else leave None
                    expire_at = None
                    if expire_at_raw:
                        try:
                            expire_at = datetime.fromisoformat(expire_at_raw)
                        except ValueError:
                            self.stdout.write(
                                self.style.ERROR(
                                    f"⚠️ Invalid expire_at in row {row['id']}: '{expire_at_raw}'"
                                )
                            )

                    # 📦 Create or update Poll object
                    Poll.objects.update_or_create(
                        id=row["id"],
                        defaults={
                            "question": row["question"],
                            "text": text_data,
                            "is_active": is_active,
                            "expire_at": expire_at,
                        },
                    )

                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Loaded poll: {row['question']}")
                    )

            # 🔧 Reset auto-increment to avoid ID collisions
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT setval('app_polls_poll_id_seq', (SELECT MAX(id) FROM app_polls_poll))"
                )

            self.stdout.write(self.style.SUCCESS("🎉 Successfully loaded polls data"))

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"📁 CSV file not found at {csv_file_path}")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"💥 Error loading polls: {e}"))
