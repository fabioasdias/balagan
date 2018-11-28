CREATE TABLE IF NOT EXISTS AvGeo (
    GeoID serial PRIMARY KEY,
    name text,
    geom geometry(MULTIPOLYGON,4326),
    description text
);

CREATE INDEX areaAvGeo ON AvGeo USING GIST (geom);


CREATE TABLE IF NOT EXISTS AvVars (
    VarID serial PRIMARY KEY,
    GeoID integer REFERENCES AvGeo(GeoID) ON DELETE CASCADE,
    NormalizedBy integer REFERENCES AvVars(VarID) ON DELETE CASCADE,
    name text,
    description text
);
CREATE INDEX geoAvVars ON AvVars(GeoID);

CREATE TABLE IF NOT EXISTS AvHier (
    HierID serial PRIMARY KEY,
    VarID integer REFERENCES AvVars(VarID) ON DELETE CASCADE,
    nodeGeom integer REFERENCES AvGeo(GeoID) ON DELETE CASCADE,
    edgeGeom integer REFERENCES AvGeo(GeoID) ON DELETE CASCADE,
    maxLevel integer,
    description text
);

CREATE INDEX avHierVar ON AvHier(VarID);
CREATE INDEX avHierNode ON AvHier(nodeGeom);
CREATE INDEX avHierEdge ON AvHier(edgeGeom);

CREATE TABLE IF NOT EXISTS Forms (
    FormID serial PRIMARY KEY,
    GeoID integer REFERENCES AvGeo(GeoID) ON DELETE CASCADE,
    centr geometry(POINT,4326),
    OriginalID text,
    geom geometry(MULTIPOLYGON,4326)
);
CREATE INDEX FormsIndex ON Forms USING GIST (geom);
CREATE INDEX centrIndex ON Forms USING GIST (centr);
CREATE INDEX origIndex ON Forms(OriginalID);
CREATE INDEX geoIndex ON Forms(GeoID);

CREATE TABLE IF NOT EXISTS SimpForm(
    FormID serial PRIMARY KEY,
    GeoID integer REFERENCES AvGeo(GeoID) ON DELETE CASCADE,
    centr geometry(POINT,4326),
    OriginalID text,
    geom geometry(MULTIPOLYGON,4326)
);
CREATE INDEX SimpFormIndex ON SimpForm USING GIST (geom);
CREATE INDEX ScentrIndex ON SimpForm USING GIST (centr);
CREATE INDEX SorigIndex ON SimpForm(OriginalID);
CREATE INDEX SgeoIndex ON SimpForm(GeoID);



CREATE TABLE IF NOT EXISTS Variables (
    VarID integer REFERENCES AvVars(VarID) ON DELETE CASCADE,
    FormID integer REFERENCES Forms(FormID) ON DELETE CASCADE,
    val numeric,
    normVal numeric,
    day timestamp,
    PRIMARY KEY (VarID, FormID)
);

CREATE INDEX formIndex ON Variables(FormID);
CREATE INDEX VarIDIndex ON Variables(VarID);

CREATE TABLE IF NOT EXISTS Edges (
    EdgeID serial PRIMARY KEY,
    HierID integer REFERENCES AvHier(HierID) ON DELETE CASCADE,
    Node1 integer REFERENCES Forms(FormID) ON DELETE CASCADE,
    Node2 integer REFERENCES Forms(FormID) ON DELETE CASCADE,
    level integer,
    scale numeric
);

CREATE INDEX hierIndex ON Edges(HierID);
  
CREATE TABLE IF NOT EXISTS uploadlog (
    tableName text PRIMARY KEY,
    uuid text,
    created timestamp,
    fname text,
    ip inet,
    done boolean
);

CREATE INDEX logUuid on uploadlog(uuid);

CREATE SCHEMA tempData;
