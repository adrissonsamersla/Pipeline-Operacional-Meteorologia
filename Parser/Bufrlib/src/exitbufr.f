	SUBROUTINE EXITBUFR

C$$$  SUBPROGRAM DOCUMENTATION BLOCK
C
C SUBPROGRAM:    EXITBUFR
C   PRGMMR: ATOR             ORG: NCEP       DATE: 2015-03-02
C
C ABSTRACT:  THIS SUBROUTINE FREES ALL DYNAMICALLY-ALLOCATED MEMORY,
C   CLOSES ALL LOGICAL UNITS THAT ARE OPEN TO THE BUFR ARCHIVE LIBRARY,
C   AND RESETS THE LIBRARY TO ALL OF ITS DEFAULT SETTINGS AS THOUGH IT
C   HAD NEVER BEEN CALLED.  THIS ALLOWS AN APPLICATION PROGRAM TO
C   POTENTIALLY RE-ALLOCATE MEMORY ALL OVER AGAIN WITHIN THE BUFR
C   ARCHIVE LIBRARY VIA A NEW SUBSEQUENT SERIES OF CALLS TO
C   SUBROUTINES ISETPRM AND OPENBF.
C
C   NOTE THAT ONCE THIS SUBROUTINE IS CALLED, THE ENTIRE BUFR ARCHIVE
C   LIBRARY IS UNUSABLE FOR THE REMAINDER OF THE LIFE OF THE
C   APPLICATION PROGRAM, UNLESS AND UNTIL SUBROUTINE OPENBF IS
C   CALLED TO ONCE AGAIN DYNAMICALLY ALLOCATE NEW ARRAY SPACE.
C
C PROGRAM HISTORY LOG:
C 2015-03-02  J. ATOR    -- ORIGINAL AUTHOR
C
C USAGE:    CALL EXITBUFR
C
C REMARKS:
C    THIS ROUTINE CALLS:        ARDLLOCF  CLOSBF  DLLOCTBF
C    THIS ROUTINE IS CALLED BY: None
C                               Normally called only by application
C                               programs.
C
C ATTRIBUTES:
C   LANGUAGE: FORTRAN
C   MACHINE:  PORTABLE TO ALL PLATFORMS
C
C$$$

	USE MODA_STBFR
	USE MODA_IFOPBF
	USE MODA_S01CM
	
	INCLUDE 'bufrlib.prm'

	COMMON /TABLEF/ CDMF

	CHARACTER*1 CDMF

C-----------------------------------------------------------------------
C-----------------------------------------------------------------------

C	Close any logical units that are open to the library.

	DO JJ = 1, NFILES
	  IF ( IOLUN(JJ) .NE. 0 ) CALL CLOSBF( ABS(IOLUN(JJ)) )
	END DO

C	Deallocate all allocated memory.

	CALL ARDLLOCF

	IF ( CDMF .EQ. 'Y' ) CALL DLLOCTBF

C	Reset the library.

	NS01V = 0
	IFOPBF = 0

	RETURN
	END
