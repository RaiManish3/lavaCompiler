interface intf
begin
    function::int kvm(String x);
end
class Main implements intf
begin

    function::void main()
    begin
        print("Main");
        return;
    end
    --function::int kvm(String x)begin 
    --return 3;
--end
end
