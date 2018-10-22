/* Sorting function in assembly */


/* -----------------Memory Section-------------------*/

.data
a: .skip 64 /*assign 64 reserve 64 bytes of data for 16 entries*/

/* --------------------------------------------------*/

/*----------------Code Section ---------------------*/
.text
.global main
main:
	mov r0, #2
	bx lr

/*---------------------------------------------------*/
