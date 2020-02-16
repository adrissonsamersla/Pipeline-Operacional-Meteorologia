      FUNCTION LSTJPB(NODE,LUN,JBTYP)

C$$$  SUBPROGRAM DOCUMENTATION BLOCK
C
C SUBPROGRAM:    LSTJPB
C   PRGMMR: WOOLLEN          ORG: NP20       DATE: 1994-01-06
C
C ABSTRACT: THIS FUNCTION SEARCHES BACKWARDS, BEGINNING FROM A GIVEN
C   NODE WITHIN THE JUMP/LINK TABLE, UNTIL IT FINDS THE MOST RECENT
C   NODE OF TYPE JBTYP.  THE INTERNAL JMPB ARRAY IS USED TO JUMP
C   BACKWARDS WITHIN THE JUMP/LINK TABLE, AND THE FUNCTION RETURNS
C   THE TABLE INDEX OF THE FOUND NODE.  IF THE INPUT NODE ITSELF IS
C   OF TYPE JBTYP, THEN THE FUNCTION SIMPLY RETURNS THE INDEX OF THAT
C   SAME NODE. 
C
C PROGRAM HISTORY LOG:
C 1994-01-06  J. WOOLLEN -- ORIGINAL AUTHOR
C 1998-07-08  J. WOOLLEN -- REPLACED CALL TO CRAY LIBRARY ROUTINE
C                           "ABORT" WITH CALL TO NEW INTERNAL BUFRLIB
C                           ROUTINE "BORT"
C 1999-11-18  J. WOOLLEN -- THE NUMBER OF BUFR FILES WHICH CAN BE
C                           OPENED AT ONE TIME INCREASED FROM 10 TO 32
C                           (NECESSARY IN ORDER TO PROCESS MULTIPLE
C                           BUFR FILES UNDER THE MPI)
C 2003-11-04  S. BENDER  -- ADDED REMARKS/BUFRLIB ROUTINE
C                           INTERDEPENDENCIES
C 2003-11-04  D. KEYSER  -- MAXJL (MAXIMUM NUMBER OF JUMP/LINK ENTRIES)
C                           INCREASED FROM 15000 TO 16000 (WAS IN
C                           VERIFICATION VERSION); UNIFIED/PORTABLE FOR
C                           WRF; ADDED DOCUMENTATION (INCLUDING
C                           HISTORY); OUTPUTS MORE COMPLETE DIAGNOSTIC
C                           INFO WHEN ROUTINE TERMINATES ABNORMALLY
C 2009-03-31  J. WOOLLEN -- ADDED ADDITIONAL DOCUMENTATION
C 2014-12-10  J. ATOR    -- USE MODULES INSTEAD OF COMMON BLOCKS
C
C USAGE:    LSTJPB (NODE, LUN, JBTYP)
C   INPUT ARGUMENT LIST:
C     NODE     - INTEGER: JUMP/LINK TABLE INDEX OF ENTRY TO BEGIN
C                SEARCHING BACKWARDS FROM
C     LUN      - INTEGER: I/O STREAM INDEX INTO INTERNAL MEMORY ARRAYS
C     JBTYP    - CHARACTER*(*): TYPE OF NODE FOR WHICH TO SEARCH
C
C   OUTPUT ARGUMENT LIST:
C     LSTJPB   - INTEGER: INDEX OF FIRST NODE OF TYPE JBTYP FOUND BY
C                JUMPING BACKWARDS FROM INPUT NODE 
C                  0 = NO SUCH NODE FOUND
C
C REMARKS:
C
C    SEE THE DOCBLOCK IN BUFR ARCHIVE LIBRARY SUBROUTINE TABSUB FOR AN
C    EXPLANATION OF THE VARIOUS NODE TYPES PRESENT WITHIN AN INTERNAL
C    JUMP/LINK TABLE 
C
C    THIS ROUTINE CALLS:        BORT
C    THIS ROUTINE IS CALLED BY: GETWIN   IGETRFEL NEVN     NEWWIN
C                               NXTWIN   PARUSR   STRBTM   TRYBUMP
C                               UFBRW
C                               Normally not called by any application
C                               programs.
C
C ATTRIBUTES:
C   LANGUAGE: FORTRAN 77
C   MACHINE:  PORTABLE TO ALL PLATFORMS
C
C$$$

      USE MODA_MSGCWD
      USE MODA_TABLES

      INCLUDE 'bufrlib.prm'

      CHARACTER*(*) JBTYP
      CHARACTER*128 BORT_STR

C----------------------------------------------------------------------
C----------------------------------------------------------------------

      IF(NODE.LT.INODE(LUN)) GOTO 900
      IF(NODE.GT.ISC(INODE(LUN))) GOTO 901

      NOD = NODE

C  FIND THIS OR THE PREVIOUS "JBTYP" NODE
C  --------------------------------------

10    IF(TYP(NOD).NE.JBTYP) THEN
         NOD = JMPB(NOD)
         IF(NOD.NE.0) GOTO 10
      ENDIF

      LSTJPB = NOD

C  EXITS
C  -----

      RETURN
900   WRITE(BORT_STR,'("BUFRLIB: LSTJPB - TABLE NODE (",I7,") IS OUT '//
     . 'OF BOUNDS, < LOWER BOUNDS (",I7,"); TAG IS ",A10)')
     . NODE,INODE(LUN),TAG(NODE)
      CALL BORT(BORT_STR)
901   WRITE(BORT_STR,'("BUFRLIB: LSTJPB - TABLE NODE (",I7,") IS OUT '//
     . 'OF BOUNDS, > UPPER BOUNDS (",I7,"); TAG IS ",A10)')
     . NODE,ISC(INODE(LUN)),TAG(NODE)
      CALL BORT(BORT_STR)
      END