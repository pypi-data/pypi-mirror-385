import os
import shutil
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Django management command to create a Django app inside the 'apps/' folder.
    
    Usage:
        python manage.py startsubapp [app_name]
    
    Example:
        python manage.py startsubapp accounts
        
    This will create the app in: apps/accounts/
    """
    
    help = "Create a Django app inside the 'apps/' folder (e.g., python manage.py startsubapp accounts)"

    def add_arguments(self, parser):
        parser.add_argument(
            "app_name",
            type=str,
            help="Name of the app to create inside apps/ folder"
        )

    def handle(self, *args, **options):
        app_name = options["app_name"]
        base_dir = os.getcwd()
        apps_folder = os.path.join(base_dir, "apps")
        target_path = os.path.join(apps_folder, app_name)
        temp_path = os.path.join(base_dir, app_name)

        # Validation
        if "." in app_name:
            raise CommandError(
                f"❌ Dots are not allowed in app name. Use simple name like 'accounts' instead of '{app_name}'."
            )

        if os.path.exists(target_path):
            raise CommandError(
                f"❌ App '{app_name}' already exists in {target_path}"
            )

        if os.path.exists(temp_path):
            raise CommandError(
                f"❌ Temporary path {temp_path} already exists. Please remove it first."
            )

        try:
            # Ensure apps/ folder exists
            os.makedirs(apps_folder, exist_ok=True)
            self.stdout.write(
                self.style.WARNING(f"📁 Ensuring 'apps' folder exists at {apps_folder}")
            )

            # Create app temporarily in root
            self.stdout.write(
                self.style.WARNING(f"🔧 Creating app '{app_name}' in temporary location...")
            )
            call_command("startapp", app_name)

            # Move app to apps/ folder
            self.stdout.write(
                self.style.WARNING(f"📦 Moving app to apps/{app_name}...")
            )
            shutil.move(temp_path, target_path)

            # Ensure __init__.py exists
            init_file = os.path.join(target_path, "__init__.py")
            if not os.path.exists(init_file):
                open(init_file, "w").close()
                self.stdout.write(
                    self.style.WARNING(f"📝 Created __init__.py in apps/{app_name}")
                )

            # Update apps.py to use correct app path
            apps_py_path = os.path.join(target_path, "apps.py")
            if os.path.exists(apps_py_path):
                with open(apps_py_path, "r", encoding="utf-8") as f:
                    apps_content = f.read()

                # Replace the default name with the correct path
                updated_content = apps_content.replace(
                    f"name = '{app_name}'",
                    f"name = 'apps.{app_name}'"
                )

                with open(apps_py_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)

                self.stdout.write(
                    self.style.WARNING(f"✏️  Updated apps.py with correct app path")
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ App '{app_name}' created successfully inside 'apps/{app_name}'"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"📌 Don't forget to add 'apps.{app_name}' to INSTALLED_APPS in settings.py"
                )
            )

        except Exception as e:
            # Cleanup on error
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            
            raise CommandError(
                f"❌ Error creating app: {str(e)}"
            )
