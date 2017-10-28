#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Functions for handling data caches

(c) The James Hutton Institute 2017
Author: Leighton Pritchard

Contact: leighton.pritchard@hutton.ac.uk
Leighton Pritchard,
Information and Computing Sciences,
James Hutton Institute,
Errol Road,
Invergowrie,
Dundee,
DD6 9LH,
Scotland,
UK

The MIT License

Copyright (c) 2017 The James Hutton Institute

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import sqlite3


# SQL QUERIES
# ===========
# The SQL below mediates cache database creation, update, and querying. It's
# up here to make reading the code easier.
#
# The intention is that the cache holds relevant information about sequences
# so that we can pick up in case of download failures (a real problem for us).
#
# The main table is seqdata, which holds input sequence accessions, and 1:1
# data for that accession.
#
# accession     - the input sequence accession, pulled from the FASTA sequence
#                 (.id attribute)
# aa_query      - a query term used for searching against the protein db or
#                 protein_nuccore link db. For NCBI sequences this is the
#                 accession.
# nt_query      - a query term used for searching against the nucleotide db.
#                 For Uniprot sequences this is provided in the GN= field
#                 (gene name), but for NCBI sequences we need to run a
#                 preliminary search to populate it.
#
# The elink table holds a cache for results of searching query_term against
# protein_nuccore to identify corresponding nucleotide UIDs. This is only
# needed when input sequences are NCBI (UniProt GNs can be used to query
# for nucleotide sequences directly.
#
# The nt_uid_acc table has a *:* relationship with seqdata. Each input
# sequence may correspond to more than one nucleotide database entry at NCBI.
# We need to identify the corresponding UID and accession for each one. Both
# UID and accession are required, as we will be downloading GenBank entries
# in batch form, and these contain the accession but not the UID in their
# headers.
# The *:* relationship is mediated by the seq_nt table, which references
# the seqdata accession (unique to input sequence) and the nt_uid_acc
# accession (unique to NCBI nucleotide sequence).


# Create tables
SQL_CREATEDB = """
    DROP TABLE IF EXISTS seqdata;
    CREATE TABLE seqdata (accession TEXT PRIMARY KEY NOT NULL,
                          aa_query TEXT,
                          nt_query TEXT
                         );
    DROP TABLE IF EXISTS elink;
    DROP TABLE IF EXISTS seq_nt;
    CREATE TABLE seq_nt (seq_nt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                         accession TEXT NOT NULL,
                         uid TEXT NOT NULL,
                         FOREIGN KEY(accession) REFERENCES seqdata(accession),
                         FOREIGN KEY(uid) REFERENCES nt_uid_acc(uid)
                        );
    DROP TABLE IF EXISTS nt_uid_acc;
    CREATE TABLE nt_uid_acc (uid TEXT PRIMARY KEY NOT NULL,
                             accession TEXT
                            );
    DROP TABLE IF EXISTS gb_headers;
    CREATE TABLE gb_headers (accession TEXT PRIMARY KEY NOT NULL,
                             length INTEGER NOT NULL,
                             organism TEXT NOT NULL,
                             taxonomy TEXT NOT NULL,
                             date TEXT NOT NULL,
                             FOREIGN KEY (accession) REFERENCES nt_uid_acc(accession)
                            );
"""

# Add a new sequence to seqdata
SQL_ADDSEQ = """
    INSERT INTO seqdata (accession, aa_query, nt_query)
           VALUES (?, ?, ?);
"""

SQL_ADD_GBHEADER = """
    INSERT INTO gb_headers (accession, length, organism,
                            taxonomy, date)
           VALUES (?, ?, ?, ?, ?);
"""

# Get queries for a seqdata row
SQL_GET_SEQDATA_QUERIES = """
    SELECT nt_query, aa_query FROM seqdata
           WHERE accession=?;
"""

# Get nt query for a seqdata row
SQL_GET_SEQDATA_NTQUERY = """
    SELECT nt_query FROM seqdata
           WHERE accession=?;
"""

# Get known nt UIDs for a sequence accession
SQL_GET_NT_UIDS = """
    SELECT uid FROM seq_nt
           WHERE accession=?;
"""

# Add nt UID for a sequence accession
SQL_ADD_NT_UID = """
    INSERT INTO nt_uid_acc (uid, accession)
           VALUES (?, ?);
"""

# Add linker between seqdata and nt_uid_acc
SQL_ADD_SEQDATA_NT_LINK = """
    INSERT INTO seq_nt (accession, uid)
           VALUES (?, ?);
"""

# Get all nt UIDs
SQL_GET_UIDS = """
    SELECT uid FROM nt_uid_acc;
"""

# Get all nt UIDs with no GenBank accession
SQL_GET_NOACC_UIDS = """
    SELECT uid FROM nt_uid_acc
           WHERE accession IS NULL;
"""


# Get all nt UIDs with no associated GenBank header
SQL_GET_NOGBHEAD_UIDS = """
    SELECT uid FROM nt_uid_acc
           WHERE accession NOT IN
                 (SELECT accession FROM gb_headers);
"""

# Update nt_uid_acc row with accession
SQL_UPDATE_UID_ACC = """
    UPDATE nt_uid_acc
           SET accession=? WHERE uid=?;
"""


# Initialise SQLite cache
def initialise_dbcache(path):
    """Initialise SQLite cache.

    path     - path to SQLite3 database cache
    """
    conn = sqlite3.connect(path)
    with conn:
        cur = conn.cursor()
        cur.executescript(SQL_CREATEDB)


def add_input_sequence(cachepath, accession, aa_query, nt_query):
    """Populate a row of the seqdata table in cache.

    accession    - unique ID for input sequence
    aa_query     - query term for searching protein or
                   protein_nuccore
    nt_query     - query term for searching nucleotide
    """
    conn = sqlite3.connect(cachepath)
    with conn:
        cur = conn.cursor()
        cur.execute(SQL_ADDSEQ, (accession, aa_query, nt_query))
    return cur.lastrowid


def has_query(cachepath, accession):
    """Returns True if a seqdata row has any query."""
    conn = sqlite3.connect(cachepath)
    with conn:
        cur = conn.cursor()
        cur.execute(SQL_GET_SEQDATA_QUERIES, (accession, ))
    if cur.fetchone() == (None, None):
        return False
    return True


def has_nt_query(cachepath, accession):
    """Returns True if a seqdata row has an nt query."""
    conn = sqlite3.connect(cachepath)
    with conn:
        cur = conn.cursor()
        cur.execute(SQL_GET_SEQDATA_NTQUERY, (accession, ))
    if cur.fetchone() is None:
        return False
    return True


def get_nt_query(cachepath, accession):
    """Returns nt query for a seqdata row."""
    conn = sqlite3.connect(cachepath)
    with conn:
        cur = conn.cursor()
        cur.execute(SQL_GET_SEQDATA_NTQUERY, (accession, ))
    return cur.fetchone()


def has_ncbi_uid(cachepath, accession):
    """Returns True if seq accession has at least one nt UID."""
    conn = sqlite3.connect(cachepath)
    with conn:
        cur = conn.cursor()
        cur.execute(SQL_GET_NT_UIDS, (accession, ))
    if cur.fetchone() is None:
        return False
    return True


def add_ncbi_uids(cachepath, accession, uids):
    """Add collection of nt UIDs to cache for a record."""
    conn = sqlite3.connect(cachepath)
    results = []
    with conn:
        cur = conn.cursor()
        for uid in uids:
            cur.execute(SQL_ADD_NT_UID, (uid, None))
            results.append(cur.fetchone())
            cur.execute(SQL_ADD_SEQDATA_NT_LINK, (accession, uid))
    return results


def get_nt_uids(cachepath):
    """Return list of nt UIDs."""
    conn = sqlite3.connect(cachepath)
    with conn:
        cur = conn.cursor()
        cur.execute(SQL_GET_UIDS)
    return [uid[0] for uid in cur.fetchall()]


def get_nogbhead_nt_uids(cachepath):
    """Return list of nt UIDs with no cached GenBank header."""
    conn = sqlite3.connect(cachepath)
    with conn:
        cur = conn.cursor()
        cur.execute(SQL_GET_NOGBHEAD_UIDS)
    return [uid[0] for uid in cur.fetchall()]


def get_nt_noacc_uids(cachepath):
    """Return list of nt UIDs having no GenBank accession."""
    conn = sqlite3.connect(cachepath)
    with conn:
        cur = conn.cursor()
        cur.execute(SQL_GET_NOACC_UIDS)
    return [uid[0] for uid in cur.fetchall()]


def update_nt_uid_acc(cachepath, uid, accession):
    """Update nt UID GenBank accession."""
    conn = sqlite3.connect(cachepath)
    results = []
    with conn:
        cur = conn.cursor()
        cur.execute(SQL_UPDATE_UID_ACC, (accession, uid))
        results.append(cur.fetchone())
    return results


def add_gb_headers(cachepath, accession, length, org, taxon, date):
    """Add a new GenBank header to the cache."""
    conn = sqlite3.connect(cachepath)
    with conn:
        cur = conn.cursor()
        cur.execute(SQL_ADD_GBHEADER, (accession, length, org,
                                       taxon, date))
    return cur.fetchone()
