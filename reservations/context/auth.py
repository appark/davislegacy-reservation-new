def auth_groups(request):
    context = {
        'is_superuser': request.user.is_superuser,
        'is_manager': False,
        'is_team': False,
        'is_authenticated': request.user.is_authenticated
    }

    groups = request.user.groups.all()

    for group in groups:
        if group.name == "Manager":
            context['is_manager'] = True
        elif group.name == "Team":
            context['is_team'] = True

    return context

