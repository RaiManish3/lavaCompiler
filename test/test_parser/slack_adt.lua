

interface i1 begin
 
    function::void list();
end
 
interface i2 begin
 
    function::void list();
end
 
class link implements i1 begin
 
    int top = -1, n = 0;
    int data[] = new int[1000];
    int link[] = new int[1000];
    int NULL = 0;
 
    function::void list() begin
            InputStreamReader isr = new InputStreamReader(System.in);
            BufferedReader br = new BufferedReader(isr);
            while (true) begin
                System.out.println("list\n1.push \t 2.pop\t 3.view \t 4.return to mainmenu");
                n = Integer.parseInt(br.readLine());
                if (n == 1)
                    then
                    System.out.println("enter a no to push");
                    top=top+1;
                    data[top] = Integer.parseInt(br.readLine());
                    link[top] = top + 1;
                else
                    if (n == 2) then
                    System.out.println("enter the position to be delete");
                    Scanner in = new Scanner(System.in);
                    int pos = in.nextInt();
                    int k = data[pos];
                    data[pos] = data[pos + 1];
                    top=top-1;
                    System.out.println("poped value is" + k);
                else if (n == 3) then
                    System.out.println("the stack is");
 
                    for (int i = 0; i <= top; i=i+1) begin
                        System.out.println(data[i] + "->");
                    end
                    System.out.println("top");
                else if (n == 4) then
                    return;
                else 
                    System.out.println("enter a correct option");
                end end end end 
            end
    end
end
 
class lst implements i2 begin
 
    int top = -1, n = 0;
    int lst[] = new int[1000];
 
    function::void list() begin
            InputStreamReader isr = new InputStreamReader(System.in);
            BufferedReader br = new BufferedReader(isr);
            while (true) begin
                System.out.println("stack\n1.push \t2.pop\t 3.view\t4. return to main menu");
                n = Integer.parseInt(br.readLine());
                if (n == 1) then
                    System.out.println("enter the no to push");
                    top=top+1;
                    lst[top] = Integer.parseInt(br.readLine());
                else if (n == 2) then
                    System.out.println("enter the position to be delete");
                    Scanner in = new Scanner(System.in);
                    int pos = in.nextInt();
                    int k = lst[pos];
                    lst[pos] = lst[pos + 1];
 
                    top=top-1;
                    System.out.println("poped value is" + k);
                else if (n == 3) then
                    System.out.println("the stack is");
                    for (int i = 0; i <= top; i=i+1) begin
                        System.out.println(lst[i]);
                    end
                else 
                    System.out.println("enter a correct option");
                end end end 
            end
    end
end
 
class stack1 begin
 
    function::void main(String args[]) begin
        InputStreamReader isr = new InputStreamReader(System.in);
        BufferedReader br = new BufferedReader(isr);
        while (true) begin
            System.out.println("1.stack using linked list \n2.stack using list\n3.Exit");
            int n = Integer.parseInt(br.readLine());
            if (n == 1) then
                link o1 = new link();
                o1.list();
            else if (n == 2) then
                lst o2 = new lst();
                o2.list();
            else if (n == 3) then
                break;
            else 
                System.out.println("enter the correct option");
            end end end 
        end
    end
end
