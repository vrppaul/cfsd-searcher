from searcher.management.commands.parse_csfd import parse_actor_id_from_href


def test_parse_actor_id_from_href():
    assert parse_actor_id_from_href("/actors/123456-some-actor/") == "123456"
