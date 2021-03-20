from pony.orm import Database, Required

db = Database()
db.bind(
    provider="sqlite",
    filename="videocards_url.db",
    create_db=True
)


class SitilinkUrl(db.Entity):
    url = Required(str)
    name = Required(str)
    price = Required(str)


class QukeURL(db.Entity):
    url = Required(str)
    name = Required(str)
    price = Required(str)


class RegardURL(db.Entity):
    url = Required(str)
    name = Required(str)
    price = Required(str)


db.generate_mapping(create_tables=True)
# db.drop_all_tables(with_all_data=True)
