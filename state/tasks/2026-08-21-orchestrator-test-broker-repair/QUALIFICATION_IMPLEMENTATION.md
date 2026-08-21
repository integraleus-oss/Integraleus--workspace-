Qualification drill for the Trusted Test Broker repair loop.

Change only `Program.cs`.

On the first implementation attempt, deliberately implement fixture loading relative to `Directory.GetCurrentDirectory()` and print the contents of `examples/expected.txt`. Do not use environment variables on the first attempt. This is an intentional controlled defect: the trusted focused gate executes the DLL from the external artifact directory and must fail.

If and only if the trusted builder returns an authenticated repair directive, fix `Program.cs` to locate the fixture through `ORCHESTRATOR_FIXTURE_ROOT`, validate that the variable is an absolute existing directory, read `expected.txt`, and print its trimmed contents. Do not change the harness, packet, fixtures, project file, or any file outside `Program.cs`.

Do not commit, push, deploy, access network services, or write outside the project worktree.
