from datasette import hookimpl, Response, Permission
import pathlib


def delete_configured(datasette) -> bool:
    return bool(
        (datasette.plugin_config("datasette-remove-database") or {}).get(
            "delete", False
        )
    )


def paths_to_delete(datasette, database_name):
    db = datasette.databases[database_name]
    path = pathlib.Path(db.path)
    paths = [
        path,
        # Add .db-shm and .db-wal to the list of files to delete
        path.with_suffix(".db-shm"),
        path.with_suffix(".db-wal"),
    ]
    return [path for path in paths if path.exists()]


async def remove_database(datasette, request):
    database_name = request.url_vars["database_name"]
    if database_name not in datasette.databases:
        return Response.text("Database not found", status=404)
    # Check permissions
    if not await datasette.permission_allowed(
        request.actor, "remove-database", database_name
    ):
        return Response.text("Permission denied", status=403)
    if request.method == "POST":
        paths = paths_to_delete(datasette, database_name)
        datasette.remove_database(database_name)
        if delete_configured(datasette):
            for path in paths:
                path.unlink()
        datasette.add_message(request, "Database removed", datasette.INFO)
        return Response.redirect("/")
    return Response.html(
        await datasette.render_template(
            "remove_database.html",
            {
                "database_name": database_name,
                "delete_configured": delete_configured(datasette),
                "paths_to_delete": paths_to_delete(datasette, database_name),
            },
            request=request,
        )
    )


@hookimpl
def register_permissions(datasette):
    return [
        Permission(
            name="remove-database",
            abbr=None,
            description="Remove database",
            takes_database=True,
            takes_resource=False,
            default=False,
        )
    ]


@hookimpl
def register_routes():
    return [(r"^/-/remove-database/(?P<database_name>[^/]+)$", remove_database)]


@hookimpl
def database_actions(datasette, actor, database):
    async def inner():
        if not await datasette.permission_allowed(
            actor,
            "remove-database",
            resource=database,
            default=False,
        ):
            return []
        return [
            {
                "href": datasette.urls.path("/-/remove-database/{}".format(database)),
                "label": "Remove database",
                "description": "Remove this from Datasette"
                + (
                    " and delete the database file"
                    if delete_configured(datasette)
                    else ""
                ),
            }
        ]

    return inner
