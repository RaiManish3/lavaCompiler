class PalindromeTest 
begin
   function::void main(String args[])
   begin
      String reverseString="";
      Scanner scanner = new Scanner(System.in);

      System.out.println("Enter a string to check if it is a palindrome:");
      String inputString = scanner.nextLine();

      int length = inputString.length();

      for ( int i = length - 1 ; i >= 0 ; i=i-1 )
      begin
         reverseString = reverseString + inputString.charAt(i);
      end

      if (inputString.equals(reverseString))
      then
         System.out.println("Input string is a palindrome.");
      else
         System.out.println("Input string is not a palindrome.");
      end

    end
end

