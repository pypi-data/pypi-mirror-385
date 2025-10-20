import pytest

from kenallclient import model


class TestKenAllSearchResult:
    def test_fromdict(self, postalcode_search_v20221101):
        result = model.KenAllSearchResult.fromdict(postalcode_search_v20221101)
        assert result == model.KenAllSearchResult(
            version="2022-11-01",
            query="千代田",
            count=2,
            offset=0,
            limit=10,
            facets=[("/東京都/千代田区", 2)],
            data=[
                model.KenAllResultItem(
                    jisx0402="13101",
                    old_code="100",
                    postal_code="1000001",
                    prefecture_kana="トウキョウト",
                    city_kana="チヨダク",
                    town_kana="チヨダ",
                    town_kana_raw="チヨダ",
                    prefecture="東京都",
                    city="千代田区",
                    town="千代田",
                    koaza="",
                    kyoto_street="",
                    building="",
                    floor="",
                    town_partial=False,
                    town_addressed_koaza=False,
                    town_chome=False,
                    town_multi=False,
                    town_raw="千代田",
                    corporation=None,
                    prefecture_roman="Tokyo",
                    city_roman="Chiyoda-ku",
                    county="",
                    county_kana="",
                    county_roman="",
                    city_without_county_and_ward="千代田区",
                    city_without_county_and_ward_kana="チヨダク",
                    city_without_county_and_ward_roman="Chiyoda-ku",
                    city_ward="",
                    city_ward_kana="",
                    city_ward_roman="",
                    town_roman="Chiyoda",
                    town_jukyohyoji=False,
                    update_status=0,
                    update_reason=0,
                ),
                model.KenAllResultItem(
                    jisx0402="13101",
                    old_code="102",
                    postal_code="1020072",
                    prefecture_kana="トウキョウト",
                    city_kana="チヨダク",
                    town_kana="イイダバシ",
                    town_kana_raw="イイダバシ",
                    prefecture="東京都",
                    city="千代田区",
                    town="飯田橋",
                    koaza="",
                    kyoto_street="",
                    building="",
                    floor="",
                    town_partial=False,
                    town_addressed_koaza=False,
                    town_chome=True,
                    town_multi=False,
                    town_raw="飯田橋",
                    corporation=None,
                    prefecture_roman="Tokyo",
                    city_roman="Chiyoda-ku",
                    county="",
                    county_kana="",
                    county_roman="",
                    city_without_county_and_ward="千代田区",
                    city_without_county_and_ward_kana="チヨダク",
                    city_without_county_and_ward_roman="Chiyoda-ku",
                    city_ward="",
                    city_ward_kana="",
                    city_ward_roman="",
                    town_roman="Iidabashi",
                    town_jukyohyoji=False,
                    update_status=0,
                    update_reason=0,
                ),
            ],
        )

    def test_fromdict_multiple_facets(self, load_version_fixture):
        """Test AddressSearcherResponse with multiple facet values"""
        fixture = load_version_fixture(
            "2023-09-01", "postalcode_search_multiple_facets.json"
        )
        result = model.KenAllSearchResult.fromdict(fixture)

        assert result.version == "2023-09-01"
        assert result.count == 3
        assert result.facets == [
            ("/東京都/千代田区", 1),
            ("/東京都/中央区", 1),
            ("/大阪府/大阪市北区", 1),
        ]
        assert len(result.data) == 3

    def test_fromdict_no_facets(self, load_version_fixture):
        """Test AddressSearcherResponse with null facets"""
        fixture = load_version_fixture("2023-09-01", "postalcode_search_no_facets.json")
        result = model.KenAllSearchResult.fromdict(fixture)

        assert result.version == "2023-09-01"
        assert result.count == 1
        assert result.facets == []
        assert len(result.data) == 1


class TestKenAllResult:
    def test_fromdict(self, postalcode_v20221101):
        result = model.KenAllResult.fromdict(postalcode_v20221101)
        assert result == model.KenAllResult(
            version="2022-11-01",
            data=[
                model.KenAllResultItem(
                    jisx0402="13101",
                    old_code="100",
                    postal_code="1008105",
                    prefecture_kana="トウキョウト",
                    city_kana="チヨダク",
                    town_kana="オオテマチ",
                    town_kana_raw="オオテマチ",
                    prefecture="東京都",
                    city="千代田区",
                    town="大手町",
                    koaza="",
                    kyoto_street="",
                    building="新大手町ビル",
                    floor="5階",
                    town_partial=False,
                    town_addressed_koaza=False,
                    town_chome=True,
                    town_multi=False,
                    town_raw="大手町",
                    corporation=model.KenAllCorporation(
                        name="チッソ　株式会社",
                        name_kana="ﾁﾂｿ ｶﾌﾞｼｷｶﾞｲｼﾔ",
                        block_lot="２丁目２－１（新大手町ビル）",
                        block_lot_num="2-2-1",
                        post_office="銀座",
                        code_type=0,
                    ),
                    prefecture_roman="Tokyo",
                    city_roman="Chiyoda-ku",
                    county="",
                    county_kana="",
                    county_roman="",
                    city_without_county_and_ward="千代田区",
                    city_without_county_and_ward_kana="チヨダク",
                    city_without_county_and_ward_roman="Chiyoda-ku",
                    city_ward="",
                    city_ward_kana="",
                    city_ward_roman="",
                    town_roman="Otemachi",
                    town_jukyohyoji=False,
                    update_status=0,
                    update_reason=0,
                )
            ],
        )


class TestHolidaySearchResult:
    def test_fromdict(self, dummy_holiday_search_json):
        result = model.HolidaySearchResult.fromdict(dummy_holiday_search_json)
        assert result == model.HolidaySearchResult(
            data=[
                model.Holiday(
                    title="元日",
                    date="2022-01-01",
                    day_of_week=6,
                    day_of_week_text="saturday",
                ),
                model.Holiday(
                    title="成人の日",
                    date="2022-01-10",
                    day_of_week=1,
                    day_of_week_text="monday",
                ),
                model.Holiday(
                    title="建国記念の日",
                    date="2022-02-11",
                    day_of_week=5,
                    day_of_week_text="friday",
                ),
                model.Holiday(
                    title="天皇誕生日",
                    date="2022-02-23",
                    day_of_week=3,
                    day_of_week_text="wednesday",
                ),
                model.Holiday(
                    title="春分の日",
                    date="2022-03-21",
                    day_of_week=1,
                    day_of_week_text="monday",
                ),
                model.Holiday(
                    title="昭和の日",
                    date="2022-04-29",
                    day_of_week=5,
                    day_of_week_text="friday",
                ),
                model.Holiday(
                    title="憲法記念日",
                    date="2022-05-03",
                    day_of_week=2,
                    day_of_week_text="tuesday",
                ),
                model.Holiday(
                    title="みどりの日",
                    date="2022-05-04",
                    day_of_week=3,
                    day_of_week_text="wednesday",
                ),
                model.Holiday(
                    title="こどもの日",
                    date="2022-05-05",
                    day_of_week=4,
                    day_of_week_text="thursday",
                ),
                model.Holiday(
                    title="海の日",
                    date="2022-07-18",
                    day_of_week=1,
                    day_of_week_text="monday",
                ),
                model.Holiday(
                    title="山の日",
                    date="2022-08-11",
                    day_of_week=4,
                    day_of_week_text="thursday",
                ),
                model.Holiday(
                    title="敬老の日",
                    date="2022-09-19",
                    day_of_week=1,
                    day_of_week_text="monday",
                ),
                model.Holiday(
                    title="秋分の日",
                    date="2022-09-23",
                    day_of_week=5,
                    day_of_week_text="friday",
                ),
                model.Holiday(
                    title="スポーツの日",
                    date="2022-10-10",
                    day_of_week=1,
                    day_of_week_text="monday",
                ),
                model.Holiday(
                    title="文化の日",
                    date="2022-11-03",
                    day_of_week=4,
                    day_of_week_text="thursday",
                ),
                model.Holiday(
                    title="勤労感謝の日",
                    date="2022-11-23",
                    day_of_week=3,
                    day_of_week_text="wednesday",
                ),
            ]
        )


class TestHoujinSearchResult:
    def test_fromdict_with_facets(self, houjinbangou_search_v20240101):
        """Test NTACorporateInfoSearcherResponse with all facet types"""
        result = model.HoujinSearchResult.fromdict(houjinbangou_search_v20240101)

        assert result.version == "2024-01-01"
        assert result.count == 3
        assert result.offset == 0
        assert result.limit == 100

        # Check facets structure
        assert result.facets is not None
        assert "area" in result.facets
        assert "kind" in result.facets
        assert "process" in result.facets
        assert "close_cause" in result.facets

        # Check area facets
        assert result.facets["area"] == [("/東京都", 2), ("/大阪府", 1)]

        # Check kind facets
        assert result.facets["kind"] == [("/株式会社", 2), ("/有限会社", 1)]

        # Check process facets
        assert result.facets["process"] == [("/新規", 2), ("/国内所在地の変更", 1)]

        # Check close_cause facets
        assert result.facets["close_cause"] == [("/合併による解散等", 1)]

    def test_fromdict_no_facets(self, load_version_fixture):
        """Test NTACorporateInfoSearcherResponse with null facets"""
        fixture = load_version_fixture(
            "2024-01-01", "houjinbangou_search_no_facets.json"
        )
        result = model.HoujinSearchResult.fromdict(fixture)

        assert result.version == "2024-01-01"
        assert result.count == 1
        assert result.facets is not None
        assert result.facets.area is None
        assert result.facets.kind is None
        assert result.facets.process is None
        assert result.facets.close_cause is None

    def test_fromdict_empty_facets(self, load_version_fixture):
        """Test NTACorporateInfoSearcherResponse with empty facets object"""
        fixture = load_version_fixture(
            "2024-01-01", "houjinbangou_search_empty_facets.json"
        )
        result = model.HoujinSearchResult.fromdict(fixture)

        assert result.version == "2024-01-01"
        assert result.count == 1
        assert result.facets is not None
        assert result.facets.area is None
        assert result.facets.kind is None
        assert result.facets.process is None
        assert result.facets.close_cause is None

        # Test __contains__ method
        assert "area" not in result.facets
        assert "kind" not in result.facets

        # Test __getitem__ raises KeyError for missing facets
        with pytest.raises(KeyError):
            _ = result.facets["area"]
