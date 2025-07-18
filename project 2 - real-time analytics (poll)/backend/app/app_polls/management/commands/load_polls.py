import csv
import json
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
                        text_data = json.loads(row["text"])
                    except json.JSONDecodeError as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Invalid JSON in row {row['id']}: {row['text']} - {e}"
                            )
                        )
                        continue
                    Poll.objects.update_or_create(
                        id=row["id"],
                        defaults={"question": row["question"], "text": text_data},
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"Loaded poll: {row['question']}")
                    )
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT setval('app_polls_poll_id_seq', (SELECT MAX(id) FROM app_polls_poll))"
                )
            self.stdout.write(self.style.SUCCESS("Successfully loaded polls data"))
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"CSV file not found at {csv_file_path}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading polls: {e}"))
