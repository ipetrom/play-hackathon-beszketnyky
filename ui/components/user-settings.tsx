"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";

interface UserSettings {
  user_email: string;
  user_name: string;
  report_time: string;
  report_delay_days: number;
}

interface UserSettingsProps {
  userEmail: string;
  onSettingsUpdate?: () => void;
}

export function UserSettings({ userEmail, onSettingsUpdate }: UserSettingsProps) {
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    report_time: "09:00",
    report_delay_days: 1
  });

  // Load user settings
  useEffect(() => {
    loadUserSettings();
  }, [userEmail]);

  const loadUserSettings = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/users/${userEmail}`);
      if (response.ok) {
        const data = await response.json();
        setSettings(data.user);
        setFormData({
          report_time: data.user.report_time.substring(0, 5), // Convert "09:00:00" to "09:00"
          report_delay_days: data.user.report_delay_days
        });
      } else {
        toast.error("Failed to load user settings");
      }
    } catch (error) {
      console.error("Error loading settings:", error);
      toast.error("Error loading settings");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const response = await fetch(`http://localhost:8000/users/${userEmail}/settings`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          report_time: formData.report_time + ":00", // Convert "09:00" to "09:00:00"
          report_delay_days: formData.report_delay_days
        }),
      });

      if (response.ok) {
        toast.success("Settings updated successfully!");
        onSettingsUpdate?.();
        loadUserSettings(); // Reload to get updated data
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to update settings");
      }
    } catch (error) {
      console.error("Error saving settings:", error);
      toast.error("Error saving settings");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Settings</CardTitle>
          <CardDescription>Loading your preferences...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Report Settings</CardTitle>
        <CardDescription>
          Configure when and how often you want to receive automated reports
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="report_time">Report Time</Label>
          <Input
            id="report_time"
            type="time"
            value={formData.report_time}
            onChange={(e) => setFormData({ ...formData, report_time: e.target.value })}
            className="w-full"
          />
          <p className="text-sm text-gray-500">
            Time of day when you want to receive reports (24-hour format)
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="report_delay">Report Frequency</Label>
          <Select
            value={formData.report_delay_days.toString()}
            onValueChange={(value) => setFormData({ ...formData, report_delay_days: parseInt(value) })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">Daily</SelectItem>
              <SelectItem value="2">Every 2 days</SelectItem>
              <SelectItem value="3">Every 3 days</SelectItem>
              <SelectItem value="7">Weekly</SelectItem>
              <SelectItem value="14">Bi-weekly</SelectItem>
              <SelectItem value="30">Monthly</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-sm text-gray-500">
            How often you want to receive new reports
          </p>
        </div>

        <div className="flex justify-end space-x-2">
          <Button
            variant="outline"
            onClick={loadUserSettings}
            disabled={saving}
          >
            Reset
          </Button>
          <Button
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? "Saving..." : "Save Settings"}
          </Button>
        </div>

        {settings && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-sm text-gray-700 mb-2">Current Settings</h4>
            <div className="text-sm text-gray-600 space-y-1">
              <p><strong>Name:</strong> {settings.user_name}</p>
              <p><strong>Email:</strong> {settings.user_email}</p>
              <p><strong>Report Time:</strong> {settings.report_time}</p>
              <p><strong>Frequency:</strong> Every {settings.report_delay_days} day(s)</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

