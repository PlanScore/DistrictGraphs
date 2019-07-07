District Graphs API
===================

🚧 Under Construction 🚧

Block equivalency files (BEFs) are a common file format used in legislative
redistricting. They’re produced by software like DistrictBuilder, Maptitude,
and Dave’s Redistricting App. The U.S. Census publishes
[nationwide district BEFs](https://www.census.gov/geographies/mapping-files/2019/dec/rdo/116-congressional-district-bef.html).
To use a BEF in geospatial software, you first need to convert it from a list
of (identifier, district) pairs to polygons. PlanScore’s experimental
District Graphs API is here to help.

Try It
------

1.  Find a BEF to experiment with. For example, Pennsylvania published their
    [2018 remedial U.S. House plan Census Block Equivalency File](http://www.pacourts.us/news-and-statistics/cases-of-public-interest/league-of-women-voters-et-al-v-the-commonwealth-of-pennsylvania-et-al-159-mm-2017).

2.  Get a pair of URLs from the District Graphs API:

        HTTP GET https://dgraphs.planscore.org/upload_file
        
    Response:
    
        {
          "assignments_url": "https://districtgraphs.s3.amazonaws.com/assignments/...",
          "districts_url": "https://dgraphs.planscore.org/read_file?filepath=...{&layer}"
        }
    
4.  Upload your BEF to the `assignments_url`:
    
        HTTP PUT {assignments_url}
        Body: Contents of equivalency file
    
5.  Expand the `districts_url` [URI template](https://tools.ietf.org/html/rfc6570)
    with a `layer` variable, one of `tract` (Census tract), `bg` (block group), 
    or `tabblock` (Census block) and poll until `status` is `complete`:
    
        HTTP GET https://dgraphs.planscore.org/read_file?filepath=...&layer={layer}
    
    Initial response:
    
        {
            "state": "started", "token": "...", "district_ids": [ ... ], "geojson_url": null
        }
    
    Again:
    
        HTTP GET https://dgraphs.planscore.org/read_file?filepath=...&layer={layer}
    
    Completed response:
    
        {
            "state": "complete", "token": "...", "district_ids": [ ... ],
            "geojson_url": "https://districtgraphs.s3.amazonaws.com/.../districts.geojson"
        }
    
    [Example Pennsylvania response](https://dgraphs.planscore.org/read_file?filepath=assignments%2F20190707T021138.817252539Z%2Fassignments&layer=tabblock).
    
6.  The `geojson_url` will contain a GeoJSON file with outlines for each
    legislative district which can be used in GIS software like ArcGIS and QGIS
    or uploaded to PlanScore to
    [get its predicted partisan behavior](https://planscore.org/plan.html?20180219T202039.596761160Z).
    
7.  If you’re editing your BEF you can re-use these same two URLs repeatedly.
    The `assignments_url` will be valid for re-use for approximately one hour.
