from django.db import migrations

def migrate_status(apps, schema_editor):
    Teacher = apps.get_model('staffs', 'Teacher')
    status_map = {
        'active': 'a',
        'inactive': 'i',
        'on_leave': 'l',
        'resigned': 'r',
        'retired': 't',
    }

    for teacher in Teacher.objects.all():
        current_status = str(teacher.status).lower()
        
        if current_status in status_map:
            teacher.status = status_map[current_status]
            teacher.save()

def reverse_migrate_status(apps, schema_editor):
    Teacher = apps.get_model('staffs', 'Teacher')
    reverse_map = {
        'a': 'active',
        'i': 'inactive',
        'l': 'on_leave',
        'r': 'resigned',
        't': 'retired',
    }
    for teacher in Teacher.objects.all():
        if teacher.status in reverse_map:
            teacher.status = reverse_map[teacher.status]
            teacher.save()

class Migration(migrations.Migration):

    dependencies = [
        ('staffs', '0003_alter_teacher_status'), 
    ]

    operations = [
        migrations.RunPython(migrate_status, reverse_migrate_status),
    ]
