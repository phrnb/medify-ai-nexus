
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { login, verifyTwoFactor } from "@/lib/api/auth";
import { useToast } from "@/hooks/use-toast";

const formSchema = z.object({
  username: z.string().email({ message: "Please enter a valid email address" }),
  password: z.string().min(8, { message: "Password must be at least 8 characters" }),
});

const twoFactorSchema = z.object({
  code: z.string().length(6, { message: "Code must be 6 digits" }),
});

const Login = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [needsTwoFactor, setNeedsTwoFactor] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  });

  const twoFactorForm = useForm<z.infer<typeof twoFactorSchema>>({
    resolver: zodResolver(twoFactorSchema),
    defaultValues: {
      code: "",
    },
  });

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      const response = await login({
        username: values.username,
        password: values.password,
      });
      
      if (response.requires_two_factor) {
        setNeedsTwoFactor(true);
        toast({
          title: "Two-factor authentication required",
          description: "Please enter the code from your authenticator app",
        });
      } else {
        toast({
          title: "Login successful",
          description: "Welcome back!",
        });
        navigate("/");
      }
    } catch (error) {
      console.error(error);
      toast({
        title: "Login failed",
        description: "Invalid email or password",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const onTwoFactorSubmit = async (values: z.infer<typeof twoFactorSchema>) => {
    setIsLoading(true);
    try {
      await verifyTwoFactor(values.code);
      toast({
        title: "Login successful",
        description: "Welcome back!",
      });
      navigate("/");
    } catch (error) {
      console.error(error);
      toast({
        title: "Verification failed",
        description: "Invalid authentication code",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
      <Card className="w-full max-w-md mx-4">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">Medify AI Nexus</CardTitle>
          <CardDescription className="text-center">
            {needsTwoFactor ? "Enter your authentication code" : "Enter your credentials to login"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {needsTwoFactor ? (
            <Form {...twoFactorForm}>
              <form onSubmit={twoFactorForm.handleSubmit(onTwoFactorSubmit)} className="space-y-4">
                <FormField
                  control={twoFactorForm.control}
                  name="code"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Authentication Code</FormLabel>
                      <FormControl>
                        <Input placeholder="123456" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button className="w-full" type="submit" disabled={isLoading}>
                  {isLoading ? "Verifying..." : "Verify"}
                </Button>
              </form>
            </Form>
          ) : (
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="username"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input placeholder="example@example.com" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Password</FormLabel>
                      <FormControl>
                        <Input type="password" placeholder="••••••••" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button className="w-full" type="submit" disabled={isLoading}>
                  {isLoading ? "Logging in..." : "Login"}
                </Button>
              </form>
            </Form>
          )}
        </CardContent>
        <CardFooter className="flex flex-col">
          <div className="text-sm text-center text-gray-500 dark:text-gray-400 mt-4">
            Protected healthcare information system.
            <br />
            Unauthorized access is prohibited.
          </div>
        </CardFooter>
      </Card>
    </div>
  );
};

export default Login;
