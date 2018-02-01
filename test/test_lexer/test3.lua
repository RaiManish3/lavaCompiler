function int::fact(int n)
begin
	if(n==1) then
		return 1
	else
		return n*fact(n-1)
end

int c = fact(5)
