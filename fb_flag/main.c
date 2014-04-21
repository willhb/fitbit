/**********************
* 	(c)2014 William Breidenthal
*	willhb@gmail.com
*	http://www.willhb.com
*
*	About: Gets a 0-1000 int from fb_client.py and drives a PWM signal to move a servo from 0-180°. 
*	Requirements: OpenLPC2148 dev board and library.
*/

#include <stdio.h>
#include <stdio.h>
#include <math.h>
#include <lpc2148/lpc214x.h>
#include <lpc2148/openlpc.h>


int	main (void)
{
	
	FIO1DIR |= 1 << 26 | 1 << 20; //LEDs are outputs
	FIO1CLR |= 1 << 26 | 1 << 20; //Turn on LEDs
	
	FIO0DIR |= 0xFF; // bits 0 -> 7 are outputs
	FIO0CLR |= 0xFF; // turn them all on
	
	PINSEL0 = (1<<1);

	PWMTC = 0x0;
	PWMPR = 0x0;
	PWMPC = 0x0; 

	PWMMR0 = 0x130000;
	PWMMR1	= 30000;
	PWMPCR = (1<<9);
	PWMMCR = (1<<1);
	
	PWMTCR = (1<<1);
	PWMTCR = (1<<0)|(1<<3);
	
	
	delay_ms(250); 	//some hard-coded delays on startup for debugging
	FIO1SET |= 1 << 26 | 1 << 20; //Turn off LEDs
	FIO0SET |= 0xFF; // turn them all off
	delay_ms(250);

	FIO1SET |= 1 << 26 | 1 << 20;
	
	int error = 0;
	int request = 0;
	
	while(1){
		
				error = scanf("%d", &request);
				FIO1CLR |= 1 << 26 | 1 << 20;
				fflush(stdin);
				if(error == 1)
				{

					if(request > 1000)
					{
						request = 1000;
					}
				
					if(request < 0)
					{
						request = 0;
					}
				
					PWMMR1 = 30000 + request*106;
					PWMLER = 3;	
				}	
				delay_ms(50);
				FIO1SET |= 1 << 26 | 1 << 20;		
	}

}

