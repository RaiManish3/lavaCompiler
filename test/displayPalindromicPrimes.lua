class Main begin


function::boolean IsItPalin(int sPrime) begin

    int p;
    int reverse = 0;
    int psPrime=sPrime;

    while (sPrime > 0) begin
        p = sPrime % 10;
        reverse = reverse * 10 + p;
        sPrime = sPrime / 10;
    end
    --print("in isitpalindrome");
    --print(sPrime);
    --print(reverse);


    if (psPrime == reverse) then
        return true;
    end

    return false;
end


    function::boolean IsItPrime(int sPrime) begin

        --print("in isitprime");
        --print(sPrime);

        if (sPrime == 2) then
            return true;
        end

        for(int i = 2; i < sPrime; i=i+1) begin
            if((sPrime % i) == 0) then
                return false;
            end

            end

            return true;
    end

    function::void main() begin

        int startingPoint = 1;
        int startingPrime = 2;
        int printPerLine = 10;

     --   IsItPrime(startingPrime);
      --  IsItPalin(startingPrime);

      --  System.out.println("Please Enter a Number: ");
        int n = readInt();

        while (startingPoint <= n)
            begin
                if (IsItPrime(startingPrime) and IsItPalin(startingPrime) ) then
                --    System.out.print(startingPrime + " ");
                print(startingPrime);
                --print(" ");
                    --if ((startingPoint % printPerLine) == 0) then
                     --   print("\n");
                    --end

                    startingPoint=startingPoint+1;
                end

                startingPrime=startingPrime+1;
        end
        return;
    end



end
