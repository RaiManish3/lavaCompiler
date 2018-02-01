class name implements intf
begin
	String s1,s2="try";
	real r = 1.5;

	function name()
	begin
		int c = hello();
	end

	function int::hello()
	begin
	    print "Hello World"
	end
end

interface intf
begin

	hello();
end
