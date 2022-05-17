.. _ncfp-basic_use:

=========
Basic Use
=========

Given a set of protein sequences in the file ``<INPUT>.fasta`` as input, the path
to an output directory as ``<OUTPUT>``, and the user's email address [#f1]_ as ``<EMAIL>``,
the following command will query the NCBI databases for nucleotide coding sequences
corresponding to the input, and write the results to files in ``<OUTPUT>``:

.. code-block:: bash

    ncfp <INPUT>.fasta <OUTPUT> <EMAIL>

The output directory ``<OUTPUT>`` will contain at least two files: ``<OUTPUT>/ncfp_aa.fasta`` and ``<OUTPUT>/ncfp_nt.fasta``.
The ``<OUTPUT>/ncfp_aa.fasta`` file will contain sequences for which a corresponding coding sequence could
be found, and ``<OUTPUT>/ncfp_nt.aa`` will contain those coding sequences.

The sequences in ``<OUTPUT>/ncfp_nt.aa`` are trimmed and validated by ``ncfp`` to produce a conceptual
translation identical to the corresponding input protein sequence.

Any protein sequences for which a partner nucleotide coding sequence could not be found will be written
to the file ``<OUTPUT>/skipped.fas``

.. _input-sequence-formats:

----------------------
Input sequence formats
----------------------

Input protein sequences must be provided in FASTA format.

``ncfp`` expects input sequence headers to take one of two forms: "NCBI" or "UniProt". ``ncfp`` will guess at sequence format/origin on the basis of the ID and description fields. By default, sequences will be assumed to be in NCBI format unless:

* the sequence ID conforms to a UniProt UID
* the sequence ID conforms to a UniParc UID (these sequences will be skipped as we should not expect a unique coding sequence)

.. code-block:: bash

    ncfp <INPUT>.fasta <OUTPUT> <EMAIL>

^^^^^^^^^^^^^^^^^^
NCBI header format
^^^^^^^^^^^^^^^^^^

In the NCBI header format, the sequence identifier is expected to correspond to a valid NCBI protein sequence
accession, e.g.

.. code-block:: bash

    >XP_004520832.1 kunitz-type serine protease inhibitor homolog dendrotoxin I-like [Ceratitis capitata]
    MRTKFVLVFALIVCVLNGLGEAQRPAHCLQPHPQGVGRCDMLISGFFYNSERNECEQWTEEGCRVQGGHT
    YDFKEDCVNECIEIN

If a coding sequence is identified successfully, the output nucleotide sequence header will have the same
accession as a sequence identifier, e.g.

.. code-block:: bash

    >XP_004520832.1 coding sequence
    ATGAGAACTAAATTTGTTTTGGTATTCGCGCTCATTGTTTGTGTACTCAACGGTTTAGGT
    GAAGCGCAAAGACCAGCACATTGCTTACAACCACATCCACAAGGAGTTGGCCGTTGTGAT
    ATGCTTATCAGTGGTTTCTTCTATAACTCGGAGCGTAATGAGTGCGAGCAATGGACAGAG
    GAGGGCTGCCGTGTGCAGGGTGGGCACACATACGATTTCAAAGAAGATTGTGTAAATGAG
    TGCATTGAAATTAATTAA

^^^^^^^^^^^^^^^^^^^^^
UniProt header format
^^^^^^^^^^^^^^^^^^^^^

In the UniProt header format, the sequence description string is expected to correspond to a UniProt download
and contain the ``GN`` gene identifier key:value pair, e.g.

.. code-block:: bash

    >tr|A0A1V9Y7A7|A0A1V9Y7A7_9STRA Lon protease homolog OS=Thraustotheca clavata GN=THRCLA_11583 PE=3 SV=1
    MYRASSKVTSAHNDGIWSTVWTSRNQIISGSLDEVVKSWDASSSEDNAILPVVKQFPGHV
    LGTLAVTATKDGRKAATSSLDCQVRILNLESGGIEKTIDTGAGESWQLVYSPDDTFIATG
    SQQSKINLINLEQEKIVNSIPVDGKFILAVAYSPDGKHLACGTFEGIVAIYDVETGKQVQ
    KYQDRAKPVRSISYSPDGSFLLAASDDMHVNIYDVLHSSLVGSVSGHISWILSVACSPDG

If a coding sequence is identified successfully, the output nucleotide sequence header should have the gene
accession as its sequence identifier, e.g.

.. code-block:: bash

    >THRCLA_11583 coding sequence
    ATGTACCGCGCCTCGTCCAAAGTAACGTCGGCTCATAATGATGGAATCTGGAGTACTGTC
    TGGACAAGCCGCAATCAAATCATAAGTGGATCTTTGGATGAAGTGGTCAAGAGCTGGGAT
    GCGAGTAGTTCCGAGGACAATGCGATTTTGCCTGTTGTCAAGCAATTTCCAGGCCACGTT
    CTAGGCACACTGGCAGTGACTGCAACGAAAGATGGTCGAAAAGCTGCTACATCGTCTTTA

^^^^^^^^^^^^^^^^^^^^^^^
Stockholm domain format
^^^^^^^^^^^^^^^^^^^^^^^

UniProt and other sources use Stockholm format to indicate that an amino acid sequence represents a
portion of a protein (such as a domain). ``ncfp`` can recognise this format and trim the coding sequence to
correspond only to the specified region of the protein.

Stockholm format domains are indicated by the syntax ``/<start>-<stop>`` immediately following the sequence
identifier in FASTA format, e.g.

.. code-block:: bash

    >tr|B7G6L2|B7G6L2_PHATC/43-112 [subseq from] Predicted protein OS=Phaeodactylum tricornutum (strain CCAP 1055/1) GN=PHATRDRAFT_48282 PE=4 SV=1
    -----------------------------SLCV-EVAGA-SQD---DGASIFQGDCN-dG
    NKHQVFDFipaPG---TdsgFHRIRA--SHSN-KCLGVADGAL--APG-AEVVQ-

To restrict the coding sequence to the region indicated in Stockholm format, pass either the ``-s`` or ``--stockholm``
option, e.g.

.. code-block:: bash

    $ ncfp -s <INPUT>.fasta <OUTPUT> <EMAIL>
    $ ncfp --stockholm <INPUT>.fasta <OUTPUT> <EMAIL>

The output nucleotide sequence does not preserve the Stockholm format location information in the output, nor
does it preserve sequence gap symbols:

.. code-block:: bash

    >PHATRDRAFT_48282 coding sequence
    TCGCTCTGCGTGGAGGTGGCTGGAGCGAGCCAAGACGACGGGGCCTCCATATTTCAAGGG
    GATTGTAATGACGGAAACAAGCATCAAGTCTTCGACTTCATTCCTGCTCCCGGTACAGAC
    AGCGGTTTTCATCGAATTCGAGCCTCGCACTCCAACAAGTGCCTTGGCGTGGCTGATGGG
    GCTTTAGCACCTGGAGCTGAGGTAGTGCAA


-----------------------------
Use Protein IDs in the Output
-----------------------------

By default `ncfp` lists the nucleotide id retrieved from the nucleotide record in the final FASTA file 
of nucleotide sequences (if the nucleotide id could not be retrieved the protein ID is used instead). 
However, some applications require the protein sequence and associated CDS sequence to be identifiable 
by sharing the same ID, for example when backthreading nucletide sequences onto alignmened protein 
sequnces using `t-coffee`.

To use the protein IDs for the IDs of the nucleotide sequences use 
the `--use_protein_ids` flag.

.. code-block:: bash

    ncfp <INPUT>.fasta <OUTPUT> <EMAIL> --use_protein_ids


.. [#f1] The user's email address is passed to NCBI to enable them to monitor use of their service and provide support