import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Button, Input, Card } from '../../components/common';
import { registerSchema, type RegisterFormData } from '../../schemas/auth.schema';
import { useState } from 'react';
import toast from 'react-hot-toast';

export function RegisterPage() {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    try {
      // Remove confirmPassword before sending to API
      const { confirmPassword, ...registerData } = data;
      await registerUser(registerData);
      toast.success('Registration successful! Welcome!');
      navigate('/dashboard');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Registration failed. Please try again.';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Swiftor</h1>
          <p className="text-gray-600">AI-powered translation & content enhancement</p>
        </div>

        <Card>
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Create Account</h2>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              {...register('full_name')}
              type="text"
              label="Full Name"
              placeholder="John Doe"
              error={errors.full_name?.message}
              autoComplete="name"
              required
            />

            <Input
              {...register('email')}
              type="email"
              label="Email Address"
              placeholder="you@example.com"
              error={errors.email?.message}
              autoComplete="email"
              required
            />

            <Input
              {...register('password')}
              type="password"
              label="Password"
              placeholder="••••••••"
              error={errors.password?.message}
              autoComplete="new-password"
              helperText="Must be at least 8 characters with uppercase, lowercase, and number"
              required
            />

            <Input
              {...register('confirmPassword')}
              type="password"
              label="Confirm Password"
              placeholder="••••••••"
              error={errors.confirmPassword?.message}
              autoComplete="new-password"
              required
            />

            <Button
              type="submit"
              variant="primary"
              size="lg"
              fullWidth
              isLoading={isLoading}
            >
              Create Account
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </Card>

        <div className="mt-6 text-center text-xs text-gray-500">
          <p>By creating an account, you agree to our Terms of Service and Privacy Policy</p>
        </div>
      </div>
    </div>
  );
}
