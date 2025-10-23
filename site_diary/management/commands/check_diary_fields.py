from django.core.management.base import BaseCommand
from site_diary.models import DiaryEntry, LaborEntry, MaterialEntry, EquipmentEntry, DelayEntry

class Command(BaseCommand):
    help = 'Check if all diary entry fields are being saved to database'

    def handle(self, *args, **options):
        # Get the latest diary entry
        latest_entry = DiaryEntry.objects.order_by('-created_at').first()
        
        if not latest_entry:
            self.stdout.write(self.style.ERROR('No diary entries found'))
            return
        
        self.stdout.write(f"Checking latest diary entry: {latest_entry.id} - {latest_entry.entry_date}")
        
        # Check DiaryEntry fields
        self.stdout.write("\n=== DIARY ENTRY FIELDS ===")
        self.stdout.write(f"Project: {latest_entry.project}")
        self.stdout.write(f"Entry Date: {latest_entry.entry_date}")
        self.stdout.write(f"Work Description: {latest_entry.work_description[:50]}...")
        self.stdout.write(f"Progress: {latest_entry.progress_percentage}%")
        self.stdout.write(f"Weather: {latest_entry.weather_condition}")
        self.stdout.write(f"Temperature High: {latest_entry.temperature_high}")
        self.stdout.write(f"Temperature Low: {latest_entry.temperature_low}")
        self.stdout.write(f"Humidity: {latest_entry.humidity}")
        self.stdout.write(f"Wind Speed: {latest_entry.wind_speed}")
        
        # Check Labor entries
        labor_entries = LaborEntry.objects.filter(diary_entry=latest_entry)
        self.stdout.write(f"\n=== LABOR ENTRIES ({labor_entries.count()}) ===")
        for labor in labor_entries:
            self.stdout.write(f"- {labor.labor_type}: {labor.workers_count} workers")
            self.stdout.write(f"  Hours: {labor.hours_worked}, Overtime: {labor.overtime_hours}")
            self.stdout.write(f"  Hourly Rate: {labor.hourly_rate}")
            self.stdout.write(f"  Total Cost: {labor.total_cost}")
        
        # Check Material entries
        material_entries = MaterialEntry.objects.filter(diary_entry=latest_entry)
        self.stdout.write(f"\n=== MATERIAL ENTRIES ({material_entries.count()}) ===")
        for material in material_entries:
            self.stdout.write(f"- {material.material_name}: {material.quantity_delivered} {material.unit}")
            self.stdout.write(f"  Supplier: {material.supplier}")
            self.stdout.write(f"  Delivery Time: {material.delivery_time}")
            self.stdout.write(f"  Unit Cost: {material.unit_cost}")
            self.stdout.write(f"  Total Cost: {material.total_cost}")
        
        # Check Equipment entries
        equipment_entries = EquipmentEntry.objects.filter(diary_entry=latest_entry)
        self.stdout.write(f"\n=== EQUIPMENT ENTRIES ({equipment_entries.count()}) ===")
        for equipment in equipment_entries:
            self.stdout.write(f"- {equipment.equipment_name}: {equipment.hours_operated} hours")
            self.stdout.write(f"  Operator: {equipment.operator_name}")
            self.stdout.write(f"  Fuel Consumption: {equipment.fuel_consumption}L")
            self.stdout.write(f"  Rental Cost/Hour: {equipment.rental_cost_per_hour}")
            self.stdout.write(f"  Total Cost: {equipment.total_rental_cost}")
        
        # Check Delay entries
        delay_entries = DelayEntry.objects.filter(diary_entry=latest_entry)
        self.stdout.write(f"\n=== DELAY ENTRIES ({delay_entries.count()}) ===")
        for delay in delay_entries:
            self.stdout.write(f"- {delay.category}: {delay.duration_hours} hours")
            self.stdout.write(f"  Start Time: {delay.start_time}")
            self.stdout.write(f"  End Time: {delay.end_time}")
            self.stdout.write(f"  Impact: {delay.impact_level}")
            self.stdout.write(f"  Description: {delay.description[:50]}...")
        
        self.stdout.write(self.style.SUCCESS('\nField check completed!'))