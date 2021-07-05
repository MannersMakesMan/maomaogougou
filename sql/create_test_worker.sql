SET @wokerip = '192.168.14.111';
set @time=now();
INSERT INTO autiomatic.VmServer(create_time, update_time, Virtual_machine_IP) VALUES (@time, @time, @wokerip);
SELECT id into @vmserverid FROM autiomatic.VmServer WHERE Virtual_machine_IP = @wokerip;
INSERT INTO autiomatic.TestVmWorker(create_time, update_time, virtual_machine_id) VALUES (@time, @time, @vmserverid)
