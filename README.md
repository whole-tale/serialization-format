# Whole Tale Export Format

Whole Tale has the ability to export Tales from the system to disk. Deciding which standard fit Whole Tale best warranted extended discussion about requirements, comparisons of existing standards, and mapping our internal representation of data into a standard's.

This document covers the Whole Tale 0.9 Tale Exporting Subsystem. It covers three sections

1. The internal architecture of exporting
1. File & Directory structure of the  exported Tale
1. Internals of the manifest.json and environment.json files

For a list of ways that Whole Tale deviates from any of the specification, refer to the Appendix.

## Use Cases
> A researcher creates a Tale and wants to export it to their local system to store and/or run locally.

> A researcher publishes a Tale to an external repository such as DataONE or Dataverse. 

> A researcher imports a Tale that was previously published to an external repository to execute in WT.

> An external repository (Dataverse/DataONE) wants to store/preserve a Tale and display defining features (e.g., provenance) to a user. The external repository expects that Whole Tale will support any given version of a Tale indefinitely.

## Future use cases:
> A researcher wants to import a Capsule, Binder or "Wild" tale

>A researcher publishes a new version of an existing Tale to an external repository

> A researcher imports a Tale that was previously exported from WT for offline editing

## Design philosophy
### Low barriers:
The system should be as familiar and support as many existing conventions as possible minimizing burden on the user to understand or modify a Tale.
Simplicity and understandability:
When users view the contents of an exported or published Tale, they should be able to understand it and potentially modify it or use the contents elsewhere.

### Interoperability (through triangulation with DataONE and Dataverse): 
Use and adopt standard formats and vocabularies (balancing with the two points above) and avoid creating new ones unless they provide significant value to the user. 
Recognize that we will likely need provider-specific adapters
Recognize that all providers do not support the same features or formats (specific examples include Atom v. EML, W3C Prov/ProvONE, JSON-LD v RDF/XML ).

### By convention: 
A fundamental principle of the Binder ecosystem is to enable researchers to operate with familiar tools and conventions.  For example, instead of requiring a Dockerfile, researchers can simply provide a requirements.txt file to install Python packages.  The developers intentionally avoided the creation of a binder.yaml that required researchers to learn a new convention.
We need to pay attention to the conventions for organizing code, data, metadata, provenance information in workflows outside of WT.
Differentiate between what we do and what we rely on external repositories 
WT is not long term storage. We rely on the repository for archival formats and preservation (e.g., BagIt v Zip)




## Quick Summary
When reading through this document, it will help to keep in mind that

1. The Tale manifest file, although tied to RO-Bundle, can be generated outside of and has use outside of exporting
1. Whole Tale's export format is a mixture of RO-Bundle, BagIt-RO and Big Data Bag with additional modifications. 
1. The relation between RO-Bundle and BagIt-RO can be confusing. BagIt-RO can be seen as an attempt to migrate RO-Bundle from a Zip centric standard to a BagIt centric standard.

```
Legend
Green Lines: Show dependencies between specifications
Black Lines: Specifications Whole Tale uses
```
![](https://i.imgur.com/UfEDMff.png)

The inclusion of RO-Bundle can be implicit through BagIt-RO. I decided to include it to explicitly clear that _some_ things come from BagIt-RO while others come from RO-Bundle.
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

# Architecture
Although Whole Tale only exports to two formats, the system was designed to easily support new additions. 

The REST service to interact with the underlying export code can be reached at the the [Girder REST Swagger Page](https://girder.wholetale.org/api/v1#!/tale/tale_exportTale).

The code related to exporting can be found in the [girder_wholetale repository](https://github.com/whole-tale/girder_wholetale) and relevant files are located in the `server/rest` and `server/lib` directories.


### Backend Implimentation


#### Exporters
Exporters are classes that hand streams of an exported Tale to the REST service. They handle creating standards-specific metadata, creating the desired directory structure, and in our case-create the bag artifacts.

![](https://i.imgur.com/LcUCU06.png)




#### The Manifest File
The manifest file is abstracted through the `Manifest` class. It's used during Tale export _and_ when the `tale/manifest` endpoint is reached.


### REST API
The REST API is used to expose the backend changes to users. Endpoints exist for both exporting the Tale and generating the manifest.
The API can be found at the [tale/](https://girder.wholetale.org/api/v1#/tale) endpoint.

#### Exporting
Tales are always exported by calling the `tale/export`endpoint.

![](https://i.imgur.com/ehHFh3s.png)

#### The Manifest File
Because Whole Tale supports linked data principles, it's important that systems have access to a linked data representation of a Tale. Exposing the manifest through the `tale/` endpoint enables other Whole Tale services and third parties to link and parse Tale objects in their systems.

![](https://i.imgur.com/UvpKeW2.png)


#### Adding Support for New Formats
To create a new export type, a new class should be created by subclassing [TaleExporter](https://github.com/whole-tale/girder_wholetale/blob/master/server/lib/exporters/__init__.py#L52) and overriding `TaleExporter.stream`.  Overriding the `stream` method gives complete control over the content inside the zip file. This means you can choose to ignore any default files (license, manifest.json, etc).

`TaleExporter` comes with a number of utility methods for working with Whole Tale's `manifest.json` and license files as well as support for hashing.

To expose the new exporter via the REST API, modify the `exportTale` method in the Tale REST endpoint.

The appropriate exporter is chosen based on a string that the user should send with the request. Define a unique string for your exporter, and return your export object's stream.

The content-type is hard coded into the API endpont as `application/zip` [here](https://github.com/whole-tale/girder_wholetale/blob/master/server/rest/tale.py#L418).  This means that any new exporter is restricted to a zip. We could make this a little more generic by making it a property of the Export class.

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

# Whole Tale's Directory & File Format 
When exporting a Tale to disk, Whole Tale uses a combination of three BagIt based specifications: Bagit-RO, RO-Bundle, and BD-Bag (see their relation in the first section). Additional changes were made that were are not part of either specification.  Most of these (if not all) are legitimate usages side-by-side with the standards.

#### Relevant Links
[BagIt Specification](https://tools.ietf.org/html/rfc8493)

[RO-Bundle Specification](https://researchobject.github.io/specifications/bundle/)

[BagIt-RO ](https://github.com/ResearchObject/bagit-ro)

[Big Data Bag](https://github.com/fair-research/bdbag)



### Structure Overview
Consider a Tale that was exported to disk. When a users extracts the contents of the zip, they will have at minimum the structure shown in the image below. The files and folders are colored based on which standard they come from. `tale_id/` is the root directory of the bag.

```
Key:

Orange: BagIt
Red: Big Data Bag
Blue: Whole Tale
Green: BagIt-RO
```
![](https://i.imgur.com/C9y2ktB.png)

In other words,
```
tale_id
├── bag-info.txt
├── bagit.txt
├── data
│   └── LICENSE
├── fetch.txt
├── manifest-md5.txt
├── manifest-sha256.txt
├── metadata
│   ├── environment.json
│   └── manifest.json
├── README.md
├── run-local.sh
├── tagmanifest-md5.txt
└── tagmanifest-sha256.txt
```


### BagIt Influence
It was decided early on that the Tales should be exported under the BagIt specification for a number of reasons. These revolve around
1. The fact that Whole Tale is involved in the publishing space where archival exchange formats are common.
1. The need for verifiable, interchangeable export objects.

#### Files from BagIt
The standard, expected BagIt files are present. The only file that was changed (in a perfectly legitimate way) was `bag-info.txt` to specify the Bagit-RO profile.

**bag-info.txt**
This file points to the BD-Bag BagIt-RO profile.
**bagit.txt**
The standard bagit file. We use 0.97.
**manifest-md5.txt**
Checksums of all the non-tag files.
**manifest-sha256.txt**
Checksums of all the non-tag files.
**tagmanifest-md5.txt**
Checksums of all the tag files.
**tagmanifest-sha256.txt**
Checksums of all the tag files.

#### Directories from BagIt
**data/**
The `data/` directory is the standard bag payload directory.


### Dependency  Analysis
Whole Tale's export format heavily relies on BagIt. The two specifications that we employ are extensions of BagIt that give solutions for our use cases. Abandoning BagIt would require finding new replacements that meet our needs.


Use Cases That Need to Be Met by Replacements:
1. An archive storing a Tale needs to have it in an archival-compliant format.
1. Users should be able to transfer Tales with external data in an efficient manner.
1. Exported Tales need to be able to be executed in local Docker containers.

### RO-Bundle & Bagit-RO Influence

The RO-Bundle specification was made with zip files in mind and _not_ BagIt.
Work was done to bring compatibility to BagIt archives and was branded under the term `BagIt-RO`.


As stated in the [BagIt-RO README](https://github.com/ResearchObject/bagit-ro#considerations) the combination of RO-Bundle and BagIt is not one to one. Instead of a `.ro/` directory at the bag root, `metadata/` is present.


Although they don't _perfectly_ align, many aspects map between the two without issue. When thinking about the two, it should be fine to consider them the same just about all the time.

#### Files from RO
**manifest.json**
The `manifest.json` file comes from the RO-Bundle specification and is unmolested by the transition to BagIt from Zip. It contains the majority of Tale metadata.

#### Directories from RO
RO-Bundle requires the addition of a single directory at the bag root, `metadata/`. This is a deviation from the RO-Bundle specification where metadata objects are placed in the `.ro/` folder.

**metadata/**
A directory at the root of the bag that holds metadata associated with the Tale. RO-Bundle specifies additional files (which are optional) that belong here although  we currently only use one: manifest.json. 

#### Dependency Analysis

The Big Data Bag implementation uses the  profile. If we were to abandon BagIt-RO, we would still be able to fall back on the BagIt profile.

The manifest file describes information according to the rules that RO-Bundle & BagIt-RO impose. To _fully_ break lose of the two specifications, we would create a new metadata files that encodes the Tale information.

### Big Data Bag Influence
The Big Data Bag specification is built around the idea of linking external data to a bag that locally exists. This allows large datasets to be exchanged using BagIt, but without transferring the actual bytes of the data. BagIt and Bagit-RO are supported by BD-Bag.

#### Files

**fetch.txt**

The purpose of fetch.txt is to allow a "bag" to be sent with a list of files that can be fetched and added to the payload -- for example, large external datasets.  This is directly related to Whole Tale's data management framework. The  BDBag project is extending BagIt to support additional protocols including Globus.


#### Dependancy Analysis

The `fetch.txt` gives us utility for using a subset of information that we already store in the `manifest.json`. It's possible to have a bag export that has the desired behaviour without external dependencies.

Although it's possible to export a Tale without the BD-Bag additions, the absence of the data fetching utility would leave users at a loss. We would additionally have to design a subsystem that replaces the fetching capabilities of the BD-Bag python utility.

The current (version 0.1.20180319) bagit-ro profile only accepts BagIt 0.97. Upgrading to 1.0 would cause conflict here.

### Whole Tale Influence
Whole tale has a few target goals that exist outside any of the specifications above. To meet these, additional changes were made outside of the RO specifications. These additions are in compliance with BagIt. 

These requirements include
1. Easily run the Tale locally
1. Give context as to what the downloaded archive is
1. Attribute licenses to data
1. Attribute Docker information 

**run-local.sh**
This file handles pulling remote data into the archive and creating a docker container with the Tale inside.
**README.md**
A brief readme that lets the user know that they're looking a Tale downloaded from Whole Tale. It additionally covers how to run the Tale.
**metadata/environment.json**
A JSON file that has information about the Tale's docker image.
**data/LICENSE**
A LICENSE file that is based on the properties set on the Tale during the time of export.
<br>
<br>
<br>
<br>
<br>
<br>


# Whole Tale's manifest.json Format


The `manifest.json` file contains most of the Tale's metadata. It contains high level information such as the name of the Tale and its description. It also contains information about the files within the Tale.

If you wish to fully understand the _structure_ of the manifest from scratch, [you first invent the universe](https://www.youtube.com/watch?v=7s664NsLeFM). If you don't have time for that, then a rudimentary understanding [OAI-ORE](http://www.openarchives.org/ore/1.0/datamodel) will get you far enough.


>  OAI-ORE is a model that allows us to aggregate objects within objects. This is handy for our application because we want to say things like "These ten data files are within the Tale" and "This manifest file describes the aggregation of Tale objects."


The RO-Bundle specification uses OAI which is why data files are placed within an `aggregates` array, which is just `ore:aggregates`.
From the ORE specification,
> The ore:aggregates relationship defines that the Resource denoted by the subject is a Resource of type ore:Aggregation. Therefore, the explicit inclusion in the Resource Map of a triple asserting the type is OPTIONAL.

This leads to the conclusion that the overall structure of the `manifest.json` file is a Resource Map. This is also why you don't see the implicit `ore:aggregation` type placed on the root.


### Keep in Mind
A few things to keep in mind while reading this section.

1. RO-Bundle aliased `@id` as `uri`.
1. RO-Bundle imports _some_ names from particular vocabularies but not necessarily all of them. (ie it says `import pav as pav` _and_ `import pav.createdBy`)
1. The manifest pulls in 15 different vocabularies. If you find yourself wondering where term you're reading came from, check the manifest's context.

### Whole Tale Specific Metadata (Things not in RO-Bundle or BD-Bag)
There is high level metadata associated with Tales that don't involve data objects. These are described with the `schema.org` vocabulary. Since they describe Tale attributes, they are at the root level in `manifest.json`. These particularly _don't_ belong as an ore aggregate because these are purely metadata tags _about the much larger structure that contains the aggregated objects_.

**schema:name**

Holds the name of the Tale.
```json
"schema:name": "FFT of Radio Astronomy Data" 
```

**schema:description**

Holds the Tale's description.
```json
"schema:description": "This Tale computes the spectral density of the power spectrum to reverse polarize the FFT of time." 
```

**schema:version**

Holds the version of the internal metadata format. This can be used to identify old Tales that need to be upgraded when importing.
```json
"schema:version": "0.8" 
```

**schema:category**

The Tale's `category` property. Because this is a string literal and _not_ and array, only one category can be used.
```json
"schema:category": "science" 
```

**schema:image**

A URL that points to an image that is used as cover art for the Tale.
```json
"schema:image": "https://avatars3.githubusercontent.com/u/13108471?s=200&v=4" 
```
**schema:identifier**

A unique UUID that Whole Tale has given to the Tale for internal identification.
```json
"schema:identifier": "f6404e5f-064c-4105-98fc-a1ba39aaea75" 
```
**schema:hasPart**

Used to declare that this Research Object (the exported Tale) uses particular software. It currently states that its uses `repo2docker`.

```json
"schema:hasPart": [
    {
        "@type": "schema:SoftwareApplication",
        "@id": "https://github.com/whole-tale/repo2docker_wholetale",
        "schema:softwareVersion": "wholetale/repo2docker_wholetale:v0.9"
    }
],
```

**schema:Author**
Whole Take allows Tale creators to add original content creators to the Tale. For example, a curator might create a Tale, but list the original paper authors as the Tale authors. An exported Tale can have anywhere from zero to many authors. 



Whole Tale uses schema:Author to describe the 
```json
"schema:author": [
        {
            "schema:familyName": "Thelen",
            "schema:givenName": "Thomas",
            "@type": "schema:Person",
            "@id": "https://orcid.org/0000-0002-1756-2128"
        }
    ],
```

**DataCite:relatedIdentifiers**

Tales hold information about where they came from and which citations they hold (in the case that a Tale is using someone's data). To encode this in the manifest, the DataCite vocabulary was chosen.

```json
{
 "relatedIdentifiers": [
    {
      "identifier": "doi:10.7910/DVN/3MJ7IR",
      "relation": "IsDerivedFrom"
    },
    {
      "identifier": "urn:some_urn",
      "relation": "Cites"
    },
    {
      "identifier": "tale_id",
      "relation": "IsIdenticalTo"
    }
  ],
}
```
**Datasets**

Although we can re-construct remote data locally by using the file URIs listed in the manifest, we also want to preserve information about the dataset that the files came from.

We allow users to assign multiple datasets to a Tale, which led to the need for something array-able. We need to be able to store multiple dataset records, so the root of the manifest doesn't suffice.

The ORE also doesn't exactly aggregate the larger datasets, so it doesn't belong in the `aggregates` section either.

Instead we defined our own word, `Datasets`, that holds a list of `schema:Dataset` objects.

The schema additions are fairly non-invasive and easy to understand, with the exception of `schemea:hasPart` and `Datasets`.

This is something that is Whole Tale specific that in hindsight, can be done better. The `Datasets` word is properly defined in the context section and third parties _should_ be able to understand this, but is not guaranteed.

```json
{
    "@type": "Dataset",
    "@id": "A resolvable URI to the dataset", 
    "identifier": "The doi or unique identifier of the dataset",
    "name": "The name of the dataset",
}

```

Known Bug:
The schema items in the dataset record should have 'schema:' prepended since they're not explicitly imported in the context.

All together, a complete `schema:Dataset` looks like
```json
{
    "Dataset": [
        {
            "identifier": "doi:10.5063/F1HM56Q3",
            "name": "Salmon-Harvest-Alaska-1995-2016",
            "@type": "Dataset",
            "@id": "doi:10.5063/F1HM56Q3"
        }
    ]
}
```




#### Adding New Terms
There may come a time when we need to serialize additional Tale properties. These will of couse fall under the "Custom Whole Tale Additions" umbrella. To stay with the current convention, the Tale property should 

1. Not fit into the RO-Bundle/Bagit-RO specifications (if it does, then use them).
1. Be described at the manifest root with the other Tale properties using the canonical/accepted vocabulary.
1. If one doesn't exist, use `schema.org` 
3. If no schema.org terms fit, explore common popular vocabularies like Dublin Core

#### Full Example
```json
{
    "schema:description": "### LIGO Detected Gravitational Waves from Black Holes\nOn September 14,2015 at 5:51 a.m. Eastern Daylight Time (09:51 UTC), the twin Laser Interferometer Gravitational-wave Observatory (LIGO) detectors, located in Livingston, Louisiana, and Hanford, Washington, USA both measured ripples in the fabric of spacetime - gravitational waves - arriving at the Earth from a cataclysmic event in the distant universe. The new Advanced LIGO detectors had just been brought into operation for their first observing run when the very clear and strong signal was captured.\n\nThis discovery comes at the culmination of decades of instrument research and development, through a world-wide effort of thousands of researchers, and made possible by dedicated support for LIGO from the National Science Foundation. It also proves a prediction made 100 years ago by Einstein that gravitational waves exist. More excitingly, it marks the beginning of a new era of gravitational wave astronomy - the possibilities for discovery are as rich and boundless as they have been with light-based astronomy.\n\nThis first detection is a spectacular discovery: the gravitational waves were produced during the final fraction of a second of the merger of two black holes to produce a single, more massive spinning black hole. This collision of two black holes had been predicted but never observed.\n\nTo learn more about the discovery and the teams that made it possible, view the [**Official Press Release**](https://www.ligo.caltech.edu/news/ligo20160211) or [**download the PDF**](https://www.ligo.caltech.edu/system/media_files/binaries/302/original/detection-press-release.pdf).To explore how LIGO works run this interactive Tale!\n\nPlease visit https://gravity.ncsa.illinois.edu/",
    "@id": "https://data.wholetale.org/api/v1/tale/5e835f81f88fdbec275c6cd8",
    "schema:version": 8,
    "schema:category": "astronomy",
    "schema:name": "LIGO Tutorial",
    "DataCite:relatedIdentifiers": [],
    "Datasets": [],
    "schema:image": "https://use.yt/upload/e922a8ac",
    "schema:identifier": "5e835f81f88fdbec275c6cd8",
    "schema:hasPart": [
        {
            "@type": "schema:SoftwareApplication",
            "@id": "https://github.com/whole-tale/repo2docker_wholetale",
            "schema:softwareVersion": "wholetale/repo2docker_wholetale:v0.9"
        }
    ],
    "Dataset": [
        {
            "identifier": "doi:10.5063/F1HM56Q3",
            "name": "Salmon-Harvest-Alaska-1995-2016",
            "@type": "Dataset",
            "@id": "doi:10.5063/F1HM56Q3"
        }
    ]
}
```

### BagIt-RO

[RO-bundle Context](https://w3id.org/bundle/context)

BagIt-RO prescribes methods for describing

1. Files that physically exist on disk
1. Files that exist remotely
1. People associated with the the Tale

#### Describing Local Files
Local file records should be placed in the root `aggregates` section.

```json
{
    "aggregates": [
        {
            "md5": "The md5 of the file",
            "size": "Size in bytes",
            "schema:license": "String representing the license type",
            "mimeType": "mimetype of the file",
            "uri": "path_to_file"
        }
    ]
}
```


Known Bug:
"schema:license" _should_ be a URL however, we save it as a string value.
Also, this may be saying "manifest.json has ___ license".


A minimal example of the LICENSE file in the `data/` directory. Note how the `uri` is a path relative to the `bag_root/metadata/` folder where the manifest is.
```json
{
    "aggregates": [
        {
            "md5": "81faaedac351f28092bd845a48c6d0a5",
            "size": 170,
            "schema:license": "CC-BY-4.0",
            "mimeType": "text/plain",
            "uri": "../data/LICENSE"
        }
    ],
    "schema:category": "science",
    .
    .
    .
}

```

#### Describing Remote Files

An example of a data file that exists at `https://raw.githubusercontent.com/whole-tale/guedesbocinsky2018/master/R/calcGDD.R`. 
```json
"aggregates": [
    {
        "size": 10004,
        "bundledAs": {
            "filename": "calcGDD.R",
            "folder": "../data/R/"
        },
        "uri": "https://raw.githubusercontent.com/whole-tale/guedesbocinsky2018/master/R/calcGDD.R"
    }
]
```

The `bundledAs` object comes from the Ro-Bundle specification and is clearly outlined there. Saving the filename and folder allows Whole Tale to properly place remote data when running locally and to reconstruct exported Tales if imported.

#### Describing Remote Files From a Repository
When remote data files come from external repositories, three things happen.
1. A `schema:Dataset`record is created and placed in `Datasets`
1. A bundle object is created for the file and placed in the `aggregates` section
1. A `schema:isPartOf` relation is placed at the bundle-level which links it to the `schema:Dataset`

Example of a file that was taken from the Dataset with DOI `doi:10.5063/F1HM56Q3`. 

```json
{
    "@id": "https://data.wholetale.org/api/v1/tale/5e5f0794351c4c0da4b49659",
    "schema:version": 8,
    "aggregates": [
        {
            "schema:isPartOf": "doi:10.5063/F1HM56Q3",
            "size": 70139,
            "bundledAs": {
                "filename": "CookInlet_harvest_sector.png",
                "folder": "../data/data/Salmon-Harvest-Alaska-1995-2016/"
            },
            "uri": "https://cn.dataone.org/cn/v2/resolve/urn:uuid:13c6bd56-297c-4a55-8d28-d722fb99ba4d"
        }
    ]
    "Datasets": [
        {
            "identifier": "doi:10.5063/F1HM56Q3",
            "name": "Salmon-Harvest-Alaska-1995-2016",
            "@type": "Dataset",
            "@id": "doi:10.5063/F1HM56Q3"
        }
    ],
    .
    .
    .
}    
```



#### Attributing Creatorship
Every exported Tale will have one creator. This is the person who created the Tale _on Whole Tale_. RO-Bundle uses a combination of PAV and FOAF to describe the creator.

Whole Tale keeps `pav:createdBy` in accordance with RO-Bundle however, deviates by describing the creator with schema terms.

```json
    "createdBy": {
        "schema:familyName": "Thelen",
        "schema:email": "thelen@nceas.ucsb.edu",
        "schema:givenName": "Thomas",
        "@type": "schema:Person",
        "@id": "thelen@nceas.ucsb.edu"
    },
```

#### Attributing Authorship
RO-Crate prescribes a way to describe authors however, Whole Tale decided to use schema (search for schema:Author))

## Whole Tale's environment.json Format
The environment.json file contains non-standard metadata about the compute environment, capturing information required by repo2docker. A controlled vocabulary is _not_ uses in this file.

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

# Appendix A: Whole Tale Deviations


# Appendix B: Changes for Next Version?



1. Turn schema:category into an array. Enables future work on the backend and UI for multuple categories.
1. Turn our `Datasets` into a `schema:Dataset` or `schema:DataCatalouge`. Gets rid of our made up `Datasets` word.
1.  Pull in vocab for md5. I meant to do this a while back.
1. schema:hasPart??
1. "schema:" needed to prefix words in `Dataset` records. Note in the snipped below that they're missing.
```json=
{
    "identifier": "doi:10.5063/F1HM56Q3",
    "name": "Salmon-Harvest-Alaska-1995-2016",
    "@type": "Dataset",
    "@id": "doi:10.5063/F1HM56Q3"
}
```

6. Move the export stream content type to the Exporter class
7. Reconsider author & creatorship use of pav+foaf



