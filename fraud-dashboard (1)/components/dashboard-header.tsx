"use client"

import { useState } from "react"
import { Bell, Menu, Search, Shield, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { ModeToggle } from "@/components/mode-toggle"
import { cn } from "@/lib/utils"

export default function DashboardHeader() {
  const [isSearchOpen, setIsSearchOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 flex h-16 items-center gap-4 border-b bg-background px-4 md:px-6">
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="outline" size="icon" className="md:hidden">
            <Menu className="h-5 w-5" />
            <span className="sr-only">Toggle Menu</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-72">
          <nav className="grid gap-6 text-lg font-medium">
            <a href="#" className="flex items-center gap-2 text-lg font-semibold">
              <Shield className="h-6 w-6" />
              <span className="font-bold">FraudGuard</span>
            </a>
            <a href="#" className="hover:text-primary">
              Overview
            </a>
            <a href="#" className="hover:text-primary">
              Analytics
            </a>
            <a href="#" className="hover:text-primary">
              Reports
            </a>
          </nav>
        </SheetContent>
      </Sheet>

      <div className="flex items-center gap-2">
        <Shield className="h-6 w-6" />
        <span className="font-bold hidden md:inline-flex">FraudGuard</span>
      </div>

      <div className={cn("hidden flex-1 items-center md:flex", isSearchOpen && "flex")}>
        {isSearchOpen ? (
          <div className="flex w-full items-center gap-2">
            <Input autoFocus placeholder="Search..." className="w-full md:w-2/3 lg:w-1/3" />
            <Button variant="ghost" size="icon" onClick={() => setIsSearchOpen(false)}>
              <X className="h-5 w-5" />
              <span className="sr-only">Close search</span>
            </Button>
          </div>
        ) : (
          <nav className="mx-6 flex items-center space-x-4 lg:space-x-6 hidden md:block">
            <a href="#" className="text-sm font-medium transition-colors hover:text-primary">
              Overview
            </a>
            <a href="#" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
              Analytics
            </a>
            <a href="#" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
              Reports
            </a>
          </nav>
        )}
      </div>

      <div className="flex items-center gap-2">
        <Button variant="outline" size="icon" className="hidden md:flex" onClick={() => setIsSearchOpen(!isSearchOpen)}>
          <Search className="h-5 w-5" />
          <span className="sr-only">Search</span>
        </Button>
        <Button variant="outline" size="icon">
          <Bell className="h-5 w-5" />
          <span className="sr-only">Notifications</span>
        </Button>
        <ModeToggle />
      </div>
    </header>
  )
}

