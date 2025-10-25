"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";

interface UserRegistrationProps {
  onUserCreated?: (userEmail: string) => void;
}

export function UserRegistration({ onUserCreated }: UserRegistrationProps) {
  const [formData, setFormData] = useState({
    user_email: "",
    user_name: "",
    report_time: "09:00",
    report_delay_days: 1
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.user_email || !formData.user_name) {
      toast.error("Please fill in all required fields");
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.user_email)) {
      toast.error("Please enter a valid email address");
      return;
    }

    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/users", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_email: formData.user_email,
          user_name: formData.user_name,
          report_time: formData.report_time + ":00", // Convert "09:00" to "09:00:00"
          report_delay_days: formData.report_delay_days
        }),
      });

      if (response.ok) {
        toast.success("Account created successfully!");
        onUserCreated?.(formData.user_email);
        // Reset form
        setFormData({
          user_email: "",
          user_name: "",
          report_time: "09:00",
          report_delay_days: 1
        });
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to create account");
      }
    } catch (error) {
      console.error("Error creating user:", error);
      toast.error("Error creating account");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Create Your Account</CardTitle>
        <CardDescription>
          Set up your Smart Tracker account to start receiving automated reports
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="user_email">Email Address *</Label>
            <Input
              id="user_email"
              type="email"
              placeholder="your.email@play.pl"
              value={formData.user_email}
              onChange={(e) => setFormData({ ...formData, user_email: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="user_name">Full Name *</Label>
            <Input
              id="user_name"
              type="text"
              placeholder="John Doe"
              value={formData.user_name}
              onChange={(e) => setFormData({ ...formData, user_name: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="report_time">Preferred Report Time</Label>
            <Input
              id="report_time"
              type="time"
              value={formData.report_time}
              onChange={(e) => setFormData({ ...formData, report_time: e.target.value })}
            />
            <p className="text-sm text-gray-500">
              When would you like to receive your daily reports?
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="report_delay">Report Frequency</Label>
            <select
              id="report_delay"
              className="w-full p-2 border border-gray-300 rounded-md"
              value={formData.report_delay_days}
              onChange={(e) => setFormData({ ...formData, report_delay_days: parseInt(e.target.value) })}
            >
              <option value={1}>Daily</option>
              <option value={2}>Every 2 days</option>
              <option value={3}>Every 3 days</option>
              <option value={7}>Weekly</option>
              <option value={14}>Bi-weekly</option>
              <option value={30}>Monthly</option>
            </select>
            <p className="text-sm text-gray-500">
              How often would you like to receive new reports?
            </p>
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={loading}
          >
            {loading ? "Creating Account..." : "Create Account"}
          </Button>
        </form>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 className="font-medium text-sm text-blue-800 mb-2">What happens next?</h4>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Your account will be created with the settings above</li>
            <li>• You can modify these settings anytime in the Settings page</li>
            <li>• Reports will be generated automatically based on your preferences</li>
            <li>• You'll receive notifications when new reports are ready</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}

