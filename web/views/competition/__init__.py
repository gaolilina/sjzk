from django.db.models import Count


def handle_competition_queryset(qs):
    return qs.values(
        'competition_id',
        'competition__name',
        'competition__time_started',
        'competition__time_ended',
        'competition__time_created',
        'competition__status',
        'competition__field',
        'competition__province',
    ).annotate(Count('competition_id'))


def competition_to_json(competition):
    return {
        'id': competition['competition_id'],
        'name': competition['competition__name'],
        'time_started': competition['competition__time_started'],
        'time_ended': competition['competition__time_ended'],
        'time_created': competition['competition__time_created'],
        'status': competition['competition__status'],
        'field': competition['competition__field'],
        'province': competition['competition__province'],
    }