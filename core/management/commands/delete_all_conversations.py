from django.core.management.base import BaseCommand
from core.models import Conversation, Message


class Command(BaseCommand):
    help = 'Supprime toutes les conversations et messages pour tester le système 1-to-1'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirmer la suppression',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  ATTENTION: Cette commande va supprimer TOUTES les conversations et messages !'
                )
            )
            self.stdout.write(
                'Pour confirmer, utilisez: python manage.py delete_all_conversations --confirm'
            )
            return

        # Compter avant suppression
        conversation_count = Conversation.objects.count()
        message_count = Message.objects.count()

        # Supprimer tous les messages d'abord (pour éviter les erreurs de clé étrangère)
        Message.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'✓ {message_count} message(s) supprimé(s)')
        )

        # Supprimer toutes les conversations
        Conversation.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'✓ {conversation_count} conversation(s) supprimée(s)')
        )

        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ Toutes les conversations et messages ont été supprimés avec succès !'
            )
        )

