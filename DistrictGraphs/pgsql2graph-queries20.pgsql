--
-- Query series used to generate tables and columns for pgsql2graph.
-- Start with Census shapefiles for tracts, VTDs, block groups, and blocks.
--

-- states that touch the outside
alter table tl_2020_us_state add column is_border boolean default false;

update tl_2020_us_state as state
set is_border = ST_Relate(state.geom, country.geom, '****1****')
from tl_2020_us as country
;

select is_border, count(1) from tl_2020_us_state group by is_border;


-- counties that touch the outside
alter table tl_2020_us_county add column is_border boolean default false;

update tl_2020_us_county as county
set is_border = CASE
    WHEN state.is_border THEN ST_Relate(county.geom, country.geom, '****1****')
    ELSE false
    END
from tl_2020_us as country, tl_2020_us_state as state
WHERE county.statefp = state.statefp
;

select is_border, count(1) from tl_2020_us_county group by is_border;


-- -- VTDs that touch the outside
-- alter table tl_2020_us_vtd20 add column is_border boolean;
-- 
-- update tl_2020_us_vtd20 as vtd
-- set is_border = CASE
--     WHEN county.is_border THEN ST_Relate(vtd.geom, country.geom, '****1****')
--     ELSE false
--     END
-- from tl_2020_us as country, tl_2020_us_county as county
-- WHERE vtd.statefp20 = state.statefp
--   AND vtd.countyfp20 = county.countyfp
-- ;
-- 
-- select is_border, count(1) from tl_2020_us_vtd20 group by is_border;


-- tracts that touch the outside
alter table tl_2020_us_tract add column is_border boolean;

update tl_2020_us_tract as tract
set is_border = CASE
    WHEN county.is_border THEN ST_Relate(tract.geom, country.geom, '****1****')
    ELSE false
    END
from tl_2020_us as country, tl_2020_us_county as county
WHERE tract.statefp = county.statefp
  AND tract.countyfp = county.countyfp
;

select is_border, count(1) from tl_2020_us_tract group by is_border;


-- block groups that touch the outside
alter table tl_2020_us_bg add column is_border boolean;

update tl_2020_us_bg as bg
set is_border = CASE
    WHEN tract.is_border THEN ST_Relate(bg.geom, country.geom, '****1****')
    ELSE false
    END
from tl_2020_us as country, tl_2020_us_tract as tract
WHERE bg.statefp = tract.statefp
  AND bg.countyfp = tract.countyfp
  AND bg.tractce = tract.tractce
;

select is_border, count(1) from tl_2020_us_bg group by is_border;


-- blocks that touch the outside
alter table tl_2020_us_tabblock20 add column is_border boolean;

update tl_2020_us_tabblock20 as block
set is_border = CASE
    WHEN tract.is_border THEN ST_Relate(block.geom, country.geom, '****1****')
    ELSE false
    END
from tl_2020_us as country, tl_2020_us_tract as tract
WHERE block.statefp20 = tract.statefp
  AND block.countyfp20 = tract.countyfp
  AND block.tractce20 = tract.tractce
;

select is_border, count(1) from tl_2020_us_tabblock20 group by is_border;


-- -- cluster on geoid20
-- alter table tl_2020_us_vtd20 alter column geoid20 set not null;
-- create index tl_2020_us_vtd20_geoid20 on tl_2020_us_vtd20 (geoid20);
-- cluster tl_2020_us_vtd20 using tl_2020_us_vtd20_geoid20;

alter table tl_2020_us_tract alter column geoid set not null;
create index tl_2020_us_tract_geoid on tl_2020_us_tract (geoid);
cluster tl_2020_us_tract using tl_2020_us_tract_geoid;

alter table tl_2020_us_bg alter column geoid set not null;
create index tl_2020_us_bg_geoid on tl_2020_us_bg (geoid);
cluster tl_2020_us_bg using tl_2020_us_bg_geoid;

alter table tl_2020_us_tabblock20 alter column geoid20 set not null;
create index tl_2020_us_tabblock20_geoid20 on tl_2020_us_tabblock20 (geoid20);
cluster tl_2020_us_tabblock20 using tl_2020_us_tabblock20_geoid20;



-- boundaries between pairs of tracts in Del Norte County, CA
drop table if exists edges_us_tract;
create table edges_us_tract
as
select tract1.geoid as geoida, tract2.geoid as geoidb,
    tract1.statefp as statefpa, tract1.countyfp as countyfpa,
    (tract1.statefp = tract2.statefp) as same_state,
    (tract1.statefp = tract2.statefp and tract1.countyfp = tract2.countyfp) as same_county
from tl_2020_us_tract as tract1
join tl_2020_us_tract as tract2
    on tract1.geom && tract2.geom
    and tract1.gid != tract2.gid
    and ST_Relate(tract1.geom, tract2.geom, 'F***1****')
--where tract1.statefp = '06'
--  and tract1.countyfp = '015'
order by tract1.geoid, tract2.geoid
;

insert into edges_us_tract
select geoid, null, statefp, countyfp, false, false
from tl_2020_us_tract
where is_border
;

-- -- boundaries between pairs of VTDs in Del Norte County, CA
-- drop table if exists edges_us_vtd20;
-- create table edges_us_vtd20
-- as
-- select vtd1.geoid20 as geoid20a, vtd2.geoid20 as geoid20b,
--     vtd1.statefp20 as statefp20a, vtd1.countyfp20 as countyfp20a,
--     (vtd1.statefp20 = vtd2.statefp20) as same_state,
--     (vtd1.statefp20 = vtd2.statefp20 and vtd1.countyfp20 = vtd2.countyfp20) as same_county
-- from tl_2020_us_vtd20 as vtd1
-- join tl_2020_us_vtd20 as vtd2
--     on vtd1.geom && vtd2.geom
--     and vtd1.gid != vtd2.gid
--     and ST_Relate(vtd1.geom, vtd2.geom, 'F***1****')
-- --where vtd1.statefp20 = '06'
-- --  and vtd1.countyfp20 = '015'
-- order by vtd1.geoid20, vtd2.geoid20
-- ;
-- 
-- insert into edges_us_vtd20
-- select geoid20, null, statefp20, countyfp20, false, false
-- from tl_2020_us_vtd20
-- where is_border
-- ;

-- boundaries between pairs of block groups in Del Norte County, CA
drop table if exists edges_us_bg;
create table edges_us_bg
as
select bg1.geoid as geoida, bg2.geoid as geoidb,
    bg1.statefp as statefpa, bg1.countyfp as countyfpa,
    (bg1.statefp = bg2.statefp) as same_state,
    (bg1.statefp = bg2.statefp and bg1.countyfp = bg2.countyfp) as same_county
from tl_2020_us_bg as bg1
join tl_2020_us_bg as bg2
    on bg1.geom && bg2.geom
    and bg1.gid != bg2.gid
    and ST_Relate(bg1.geom, bg2.geom, 'F***1****')
--where bg1.statefp = '06'
--  and bg1.countyfp = '015'
order by bg1.geoid, bg2.geoid
;

insert into edges_us_bg
select geoid, null, statefp, countyfp, false, false
from tl_2020_us_bg
where is_border
;

-- boundaries between pairs of blocks in Del Norte County, CA
drop table if exists edges_us_tabblock20;
create table edges_us_tabblock20
as
select block1.geoid20 as geoid20a, block2.geoid20 as geoid20b,
    block1.statefp20 as statefp20a, block1.countyfp20 as countyfp20a,
    (block1.statefp20 = block2.statefp20) as same_state,
    (block1.statefp20 = block2.statefp20 and block1.countyfp20 = block2.countyfp20) as same_county
from tl_2020_us_tabblock20 as block1
join tl_2020_us_tabblock20 as block2
    on block1.geom && block2.geom
    and block1.gid != block2.gid
    and ST_Relate(block1.geom, block2.geom, 'F***1****')
--where block1.statefp20 = '06'
--  and block1.countyfp20 = '015'
order by block1.geoid20, block2.geoid20
;

insert into edges_us_tabblock20
select geoid20, null, statefp20, countyfp20, false, false
from tl_2020_us_tabblock20
where is_border
;

--
alter table edges_us_tract alter column geoida set not null;
create index edges_us_tract_geoida on edges_us_tract (geoida);
create index edges_us_tract_county on edges_us_tract (statefpa, countyfpa);
cluster edges_us_tract using edges_us_tract_geoida;

-- alter table edges_us_vtd20 alter column geoid20a set not null;
-- create index edges_us_vtd20_geoid20a on edges_us_vtd20 (geoid20a);
-- create index edges_us_vtd20_county on edges_us_vtd20 (statefp20a, countyfp20a);
-- cluster edges_us_vtd20 using edges_us_vtd20_geoid20a;

alter table edges_us_bg alter column geoida set not null;
create index edges_us_bg_geoida on edges_us_bg (geoida);
create index edges_us_bg_county on edges_us_bg (statefpa, countyfpa);
cluster edges_us_bg using edges_us_bg_geoida;

alter table edges_us_tabblock20 alter column geoid20a set not null;
create index edges_us_tabblock20_geoid20a on edges_us_tabblock20 (geoid20a);
create index edges_us_tabblock20_county on edges_us_tabblock20 (statefp20a, countyfp20a);
cluster edges_us_tabblock20 using edges_us_tabblock20_geoid20a;



alter table edges_us_tabblock20 rename column geoid20a to geoida;
alter table edges_us_tabblock20 rename column geoid20b to geoidb;
alter table edges_us_tabblock20 rename column statefp20a to statefpa;
alter table edges_us_tabblock20 rename column countyfp20a to countyfpa;
alter table edges_us_tabblock20 rename to edges_us_tabblock;

alter table tl_2020_us_tabblock20 rename column statefp20 to statefp;
alter table tl_2020_us_tabblock20 rename column countyfp20 to countyfp;
alter table tl_2020_us_tabblock20 rename column tractce20 to tractce;
alter table tl_2020_us_tabblock20 rename column blockce20 to blockce;
alter table tl_2020_us_tabblock20 rename column geoid20 to geoid;
alter table tl_2020_us_tabblock20 rename column name20 to name;
alter table tl_2020_us_tabblock20 rename column mtfcc20 to mtfcc;
alter table tl_2020_us_tabblock20 rename column ur20 to ur;
alter table tl_2020_us_tabblock20 rename column uace20 to uace;
alter table tl_2020_us_tabblock20 rename column uatype20 to uatype;
alter table tl_2020_us_tabblock20 rename column funcstat20 to funcstat;
alter table tl_2020_us_tabblock20 rename column aland20 to aland;
alter table tl_2020_us_tabblock20 rename column awater20 to awater;
alter table tl_2020_us_tabblock20 rename column intptlat20 to intptlat;
alter table tl_2020_us_tabblock20 rename column intptlon20 to intptlon;
alter table tl_2020_us_tabblock20 rename to tl_2020_us_tabblock;
