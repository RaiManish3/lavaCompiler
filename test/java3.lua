interface Inf1
begin
   function::void method1();
end
interface Inf2
begin
   function::void method2();
end
class Demo implements Inf2,Inf1
begin
    function::void method1()
    begin
	System.out.println("method1");
    end
    function::void method2()
    begin
	System.out.println("method2");
    end
    function::void main(String args[])
    begin
	Inf2 obj = new Demo();
	obj.method2();
    end
end
