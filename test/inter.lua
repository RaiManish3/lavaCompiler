interface intf
begin
    function::int kvm(String x);
    function::int jkvm(String x);
    function::int kkvm(String x);
end
class Main implements intf
begin

    function::void main()
    begin
        print("Main");
        return;
    end
    function::int jkvm(String x)begin 
    return 3;
    end
    function::int kkvm(String x)begin 
    return 3;
    end
    function::int kvm(String x)begin 
    return 3;
    end
end
