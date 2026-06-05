"use client";

import { Loader2, ShieldCheck, UserCheck, UserX } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ManagedUser, listUsers, updateUser } from "@/lib/api";

export default function UsersPage() {
  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const token = useMemo(() => {
    if (typeof window === "undefined") {
      return "";
    }

    return window.localStorage.getItem("analytics_access_token") ?? "";
  }, []);

  useEffect(() => {
    async function loadUsers() {
      if (!token) {
        return;
      }

      setIsLoading(true);
      try {
        setUsers(await listUsers(token));
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Unable to load users");
      } finally {
        setIsLoading(false);
      }
    }

    void loadUsers();
  }, [token]);

  async function toggleActive(user: ManagedUser) {
    const updatedUser = await updateUser(token, user.id, { is_active: !user.is_active });
    setUsers((currentUsers) =>
      currentUsers.map((currentUser) => (currentUser.id === user.id ? updatedUser : currentUser)),
    );
  }

  return (
    <main className="min-h-screen bg-background">
      <header className="border-b bg-white px-5 py-4">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-semibold">User management</h1>
            <p className="text-sm text-muted-foreground">
              Manage access and administrative privileges.
            </p>
          </div>
          <Badge variant="secondary">{users.length} users</Badge>
        </div>
      </header>

      <section className="mx-auto max-w-7xl p-5">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-primary" aria-hidden="true" />
              Platform users
            </CardTitle>
            <CardDescription>
              {isLoading ? "Loading users..." : "Superuser access is required for this view."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-auto rounded-md border">
              <table className="w-full min-w-[720px] border-collapse text-sm">
                <thead className="bg-muted">
                  <tr>
                    <th className="border-b px-3 py-2 text-left font-semibold">User</th>
                    <th className="border-b px-3 py-2 text-left font-semibold">Status</th>
                    <th className="border-b px-3 py-2 text-left font-semibold">Role</th>
                    <th className="border-b px-3 py-2 text-right font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className="border-b last:border-b-0">
                      <td className="px-3 py-3">
                        <p className="font-medium">{user.full_name}</p>
                        <p className="text-xs text-muted-foreground">{user.email}</p>
                      </td>
                      <td className="px-3 py-3">
                        <Badge variant={user.is_active ? "secondary" : "outline"}>
                          {user.is_active ? "Active" : "Disabled"}
                        </Badge>
                      </td>
                      <td className="px-3 py-3">
                        <Badge variant={user.is_superuser ? "default" : "outline"}>
                          {user.is_superuser ? "Admin" : "User"}
                        </Badge>
                      </td>
                      <td className="px-3 py-3 text-right">
                        <Button
                          className="gap-2"
                          size="sm"
                          type="button"
                          variant="outline"
                          onClick={() => void toggleActive(user)}
                        >
                          {user.is_active ? (
                            <UserX className="h-4 w-4" aria-hidden="true" />
                          ) : (
                            <UserCheck className="h-4 w-4" aria-hidden="true" />
                          )}
                          {user.is_active ? "Disable" : "Enable"}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {isLoading ? (
              <div className="mt-4 flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                Loading
              </div>
            ) : null}
            {message ? <p className="mt-4 text-sm text-muted-foreground">{message}</p> : null}
          </CardContent>
        </Card>
      </section>
    </main>
  );
}

