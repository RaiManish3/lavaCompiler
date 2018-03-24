class BinarySearchExample
begin

   function:: void main(String args[])
   begin
      int counter, num, item, array[], first, last, middle;
      Scanner input = new Scanner(System.in);
      System.out.println("Enter number of elements:");
      num = input.nextInt();

      array = new int[num];

      System.out.println("Enter " + num + " integers");
      for (counter = 0; counter < num; counter=counter+1)
      begin
          array[counter] = input.nextInt();
      end

      System.out.println("Enter the search value:");
      item = input.nextInt();
      first = 0;
      last = num - 1;
      middle = (first + last)/2;

      while( first <= last )
      begin
         if ( array[middle] < item )
         then
           first = middle + 1;
         else
	 if ( array[middle] == item )
        then
        	System.out.println(item + " found at location " + (middle + 1) + ".");
        	break;
         else
             last = middle - 1;
         end
         middle = (first + last)/2;
      end
      end
      if ( first > last )
     then
          System.out.println(item + " is not found.\n");
     end
 end
end
