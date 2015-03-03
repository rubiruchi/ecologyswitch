

1. put the controller acting as a learning switch
2. run mininet with 4 (2 from external) hosts and 1 switch
3. connect the mininet with port 4 and 5 of Cisco switch
4. connect a host with port 1 of Cisco switch


app:
1. Ttot =  traffic from h1 + traffic from h2
2. if !(Ttot <= max_1_link_capacity){
		activate the 2nd link
		load balance between the both links
   }else{
   		disable the 2nd link
   		shutdown port on the cisco side. 
   }



