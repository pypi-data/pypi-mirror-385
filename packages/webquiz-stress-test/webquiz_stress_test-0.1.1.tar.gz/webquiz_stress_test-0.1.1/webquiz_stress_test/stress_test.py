#!/usr/bin/env python3
"""
Stress Testing Script for WebQuiz Server

This script simulates multiple concurrent users taking quizzes to test server performance.
"""

import asyncio
import argparse
import aiohttp
import time
import random
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import statistics


@dataclass
class RequestStats:
    """Track statistics for a single request type"""

    name: str
    response_times: List[float] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    errors: Dict[str, int] = field(default_factory=dict)

    def add_success(self, response_time: float):
        self.response_times.append(response_time)
        self.success_count += 1

    def add_failure(self, error: str):
        self.failure_count += 1
        self.errors[error] = self.errors.get(error, 0) + 1

    def get_stats(self) -> Dict:
        total = self.success_count + self.failure_count
        success_rate = (self.success_count / total * 100) if total > 0 else 0

        if self.response_times:
            return {
                "name": self.name,
                "total_requests": total,
                "success": self.success_count,
                "failures": self.failure_count,
                "success_rate": f"{success_rate:.2f}%",
                "avg_response_time": f"{statistics.mean(self.response_times):.3f}s",
                "min_response_time": f"{min(self.response_times):.3f}s",
                "max_response_time": f"{max(self.response_times):.3f}s",
                "median_response_time": f"{statistics.median(self.response_times):.3f}s",
            }
        else:
            return {
                "name": self.name,
                "total_requests": total,
                "success": self.success_count,
                "failures": self.failure_count,
                "success_rate": f"{success_rate:.2f}%",
            }


@dataclass
class TestStatistics:
    """Global statistics tracker"""

    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    clients_started: int = 0
    clients_completed: int = 0
    clients_failed: int = 0

    register: RequestStats = field(default_factory=lambda: RequestStats("Register"))
    update_registration: RequestStats = field(default_factory=lambda: RequestStats("Update Registration"))
    verify_user: RequestStats = field(default_factory=lambda: RequestStats("Verify User"))
    question_start: RequestStats = field(default_factory=lambda: RequestStats("Question Start"))
    submit_answer: RequestStats = field(default_factory=lambda: RequestStats("Submit Answer"))
    approve_user: RequestStats = field(default_factory=lambda: RequestStats("Approve User"))

    def mark_client_started(self):
        self.clients_started += 1

    def mark_client_completed(self):
        self.clients_completed += 1

    def mark_client_failed(self):
        self.clients_failed += 1

    def finalize(self):
        self.end_time = time.time()

    def get_summary(self) -> Dict:
        duration = (self.end_time or time.time()) - self.start_time
        return {
            "duration": f"{duration:.2f}s",
            "clients_started": self.clients_started,
            "clients_completed": self.clients_completed,
            "clients_failed": self.clients_failed,
            "completion_rate": f"{(self.clients_completed / self.clients_started * 100) if self.clients_started > 0 else 0:.2f}%",
        }


class StressClient:
    """Simulates a single user taking a quiz"""

    def __init__(
        self,
        client_id: int,
        base_url: str,
        delay_range: Tuple[float, float],
        reload_probability: float,
        update_registration_prob: float,
        master_key: Optional[str],
        stats: TestStatistics,
        wait_for_approval: bool = True,
        approval_timeout: float = 30.0,
    ):
        self.client_id = client_id
        self.base_url = base_url.rstrip("/")
        self.delay_range = delay_range
        self.reload_probability = reload_probability
        self.update_registration_prob = update_registration_prob
        self.master_key = master_key
        self.stats = stats
        self.wait_for_approval = wait_for_approval
        self.approval_timeout = approval_timeout
        self.username = f"StressTest_User_{client_id}_{int(time.time())}"
        self.user_id: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.questions: List[Dict] = []
        self.total_questions: Optional[int] = None
        self.question_order: Optional[List[int]] = None  # Randomized question order from server

    async def run(self):
        """Main client execution flow"""
        try:
            async with aiohttp.ClientSession() as session:
                self.session = session

                # Step 1: Register
                if not await self.register():
                    self.stats.mark_client_failed()
                    return

                # Step 1.5: Optionally update registration (before approval)
                if random.random() < self.update_registration_prob:
                    await self.update_registration()

                # Step 2: Wait for approval if required
                if self.wait_for_approval:
                    approved = await self.wait_for_approval_with_timeout()
                    if not approved:
                        print(f"[Client {self.client_id}] Approval timeout - exiting")
                        self.stats.mark_client_failed()
                        return

                # Step 3: Fetch quiz metadata to determine number of questions
                num_questions = await self.get_question_count()
                if num_questions == 0:
                    print(f"[Client {self.client_id}] ERROR: Could not determine question count")
                    self.stats.mark_client_failed()
                    return

                # Step 4: Answer all questions
                await self.answer_questions(num_questions)

                self.stats.mark_client_completed()
                print(f"[Client {self.client_id}] Completed quiz")

        except Exception as e:
            print(f"[Client {self.client_id}] ERROR: {type(e).__name__}: {str(e)}")
            self.stats.mark_client_failed()

    async def register(self) -> bool:
        """Register user with the server"""
        start_time = time.time()
        try:
            url = f"{self.base_url}/api/register"
            async with self.session.post(url, json={"username": self.username}) as resp:
                response_time = time.time() - start_time

                if resp.status == 200:
                    data = await resp.json()
                    self.user_id = data.get("user_id")
                    requires_approval = data.get("requires_approval", False)
                    is_approved = data.get("approved", True)

                    # Store randomized question order if provided
                    self.question_order = data.get("question_order")

                    self.stats.register.add_success(response_time)
                    print(
                        f"[Client {self.client_id}] Registered as {self.username} "
                        f"(user_id: {self.user_id}, requires_approval: {requires_approval})"
                    )

                    # If approved immediately, we can proceed
                    if is_approved:
                        self.wait_for_approval = False

                    return True
                else:
                    error_text = await resp.text()
                    self.stats.register.add_failure(f"HTTP {resp.status}")
                    print(f"[Client {self.client_id}] Registration failed: {error_text}")
                    return False

        except Exception as e:
            self.stats.register.add_failure(type(e).__name__)
            print(f"[Client {self.client_id}] Registration error: {e}")
            return False

    async def update_registration(self) -> bool:
        """Update registration data (username) before approval"""
        start_time = time.time()
        try:
            url = f"{self.base_url}/api/update-registration"
            # Update username with a modified version
            new_username = f"{self.username}_updated"
            payload = {"user_id": self.user_id, "username": new_username}

            async with self.session.put(url, json=payload) as resp:
                response_time = time.time() - start_time

                if resp.status == 200:
                    self.stats.update_registration.add_success(response_time)
                    self.username = new_username
                    print(f"[Client {self.client_id}] Updated registration to {new_username}")
                    return True
                else:
                    error_text = await resp.text()
                    self.stats.update_registration.add_failure(f"HTTP {resp.status}")
                    print(f"[Client {self.client_id}] Update registration failed: {error_text}")
                    return False

        except Exception as e:
            self.stats.update_registration.add_failure(type(e).__name__)
            print(f"[Client {self.client_id}] Update registration error: {e}")
            return False

    async def wait_for_approval_with_timeout(self) -> bool:
        """Wait for admin approval with timeout"""
        print(f"[Client {self.client_id}] Waiting for approval...")
        start_time = time.time()

        while time.time() - start_time < self.approval_timeout:
            try:
                approved = await self.check_approval_status()
                if approved:
                    print(f"[Client {self.client_id}] Approved!")
                    return True

                await asyncio.sleep(1)  # Check every second

            except Exception as e:
                print(f"[Client {self.client_id}] Error checking approval: {e}")
                await asyncio.sleep(1)

        return False

    async def check_approval_status(self) -> bool:
        """Check if user has been approved and get quiz metadata"""
        start_time = time.time()
        try:
            url = f"{self.base_url}/api/verify-user/{self.user_id}"
            async with self.session.get(url) as resp:
                response_time = time.time() - start_time

                if resp.status == 200:
                    data = await resp.json()
                    self.stats.verify_user.add_success(response_time)

                    # Extract total_questions if available
                    if "total_questions" in data:
                        self.total_questions = data["total_questions"]

                    # Extract question_order if available (for randomized quizzes)
                    if "question_order" in data and not self.question_order:
                        self.question_order = data["question_order"]

                    return data.get("approved", False)
                else:
                    self.stats.verify_user.add_failure(f"HTTP {resp.status}")
                    return False

        except Exception as e:
            self.stats.verify_user.add_failure(type(e).__name__)
            return False

    async def get_question_count(self) -> int:
        """Fetch quiz metadata to determine number of questions"""
        try:
            # If we already have the question count from verify-user, use it
            if self.total_questions is not None:
                return self.total_questions

            # Otherwise, call verify-user endpoint to get the total_questions
            url = f"{self.base_url}/api/verify-user/{self.user_id}"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.total_questions = data.get("total_questions", 0)
                    return self.total_questions
                else:
                    print(f"[Client {self.client_id}] Failed to get question count: HTTP {resp.status}")
                    return 0
        except Exception as e:
            print(f"[Client {self.client_id}] Error fetching question count: {e}")
            return 0

    async def answer_questions(self, num_questions: int):
        """Answer all questions with random delays"""

        for question_idx in range(num_questions):
            # Random delay between answers
            delay = random.uniform(*self.delay_range)
            await asyncio.sleep(delay)

            # Maybe reload (re-request data)
            if random.random() < self.reload_probability:
                await self.reload_page()

            # Determine the actual question ID to answer
            # If we have a question_order (randomized quiz), use it; otherwise sequential
            if self.question_order and question_idx < len(self.question_order):
                question_id = self.question_order[question_idx]
            else:
                question_id = question_idx + 1

            # Notify server that question started (for timing and live stats)
            await self.question_start(question_id)

            # Submit answer
            await self.submit_answer(question_id)

    async def reload_page(self):
        """Simulate page reload by re-verifying user"""
        try:
            await self.check_approval_status()
            print(f"[Client {self.client_id}] Reloaded page")
        except Exception as e:
            print(f"[Client {self.client_id}] Reload error: {e}")

    async def question_start(self, question_id: int) -> bool:
        """Notify server that user started viewing a question"""
        start_time = time.time()
        try:
            url = f"{self.base_url}/api/question-start"
            payload = {"user_id": self.user_id, "question_id": question_id}

            async with self.session.post(url, json=payload) as resp:
                response_time = time.time() - start_time

                if resp.status == 200:
                    self.stats.question_start.add_success(response_time)
                    return True
                else:
                    error_text = await resp.text()
                    self.stats.question_start.add_failure(f"HTTP {resp.status}")
                    print(f"[Client {self.client_id}] Question start failed for Q{question_id}: {error_text}")
                    return False

        except Exception as e:
            self.stats.question_start.add_failure(type(e).__name__)
            print(f"[Client {self.client_id}] Question start error for Q{question_id}: {e}")
            return False

    async def submit_answer(self, question_id: int):
        """Submit answer for a question"""
        start_time = time.time()
        try:
            url = f"{self.base_url}/api/submit-answer"
            # Random answer (0-3 for typical multiple choice)
            selected_answer = random.randint(0, 3)

            payload = {"user_id": self.user_id, "question_id": question_id, "selected_answer": selected_answer}

            async with self.session.post(url, json=payload) as resp:
                response_time = time.time() - start_time

                if resp.status == 200:
                    self.stats.submit_answer.add_success(response_time)
                    data = await resp.json()
                    print(
                        f"[Client {self.client_id}] Answered Q{question_id} "
                        f"(correct: {data.get('is_correct', 'N/A')}, time: {response_time:.3f}s)"
                    )
                else:
                    error_text = await resp.text()
                    self.stats.submit_answer.add_failure(f"HTTP {resp.status}")
                    print(f"[Client {self.client_id}] Submit answer failed: {error_text}")

        except Exception as e:
            self.stats.submit_answer.add_failure(type(e).__name__)
            print(f"[Client {self.client_id}] Submit answer error: {e}")


class AutoApprover:
    """Automatically approves users for testing with approval workflow"""

    def __init__(self, base_url: str, master_key: str, stats: TestStatistics):
        self.base_url = base_url.rstrip("/")
        self.master_key = master_key
        self.stats = stats
        self.running = False
        self.approved_users = set()

    async def run(self):
        """Run approval loop"""
        self.running = True
        async with aiohttp.ClientSession() as session:
            while self.running:
                await asyncio.sleep(0.5)  # Check twice per second
                # In a real implementation, we'd need WebSocket support
                # For now, this is a placeholder

    async def approve_user(self, user_id: str, session: aiohttp.ClientSession):
        """Approve a specific user"""
        start_time = time.time()
        try:
            url = f"{self.base_url}/api/admin/approve-user"
            headers = {"X-Master-Key": self.master_key}
            payload = {"user_id": user_id}

            async with session.put(url, headers=headers, json=payload) as resp:
                response_time = time.time() - start_time

                if resp.status == 200:
                    self.stats.approve_user.add_success(response_time)
                    self.approved_users.add(user_id)
                    print(f"[AutoApprover] Approved user {user_id}")
                    return True
                else:
                    self.stats.approve_user.add_failure(f"HTTP {resp.status}")
                    return False

        except Exception as e:
            self.stats.approve_user.add_failure(type(e).__name__)
            return False

    def stop(self):
        self.running = False


class StressTestCoordinator:
    """Coordinates multiple stress test clients"""

    def __init__(self, args):
        self.args = args
        self.stats = TestStatistics()
        self.clients: List[StressClient] = []
        self.auto_approver: Optional[AutoApprover] = None

    async def run(self):
        """Run the stress test"""
        print(f"\n{'=' * 60}")
        print(f"WebQuiz Stress Test")
        print(f"{'=' * 60}")
        print(f"Server URL: {self.args.url}")
        print(f"Number of clients: {self.args.clients}")
        print(f"Answer delay range: {self.args.delay_min}s - {self.args.delay_max}s")
        print(f"Reload probability: {self.args.reload_prob * 100}%")
        print(f"Update registration probability: {self.args.update_registration_prob * 100}%")
        print(f"Wait for approval: {self.args.wait_for_approval}")
        if self.args.wait_for_approval and self.args.master_key:
            print(f"Auto-approve enabled: Yes")
        print(f"{'=' * 60}\n")

        # Create clients
        for i in range(self.args.clients):
            client = StressClient(
                client_id=i + 1,
                base_url=self.args.url,
                delay_range=(self.args.delay_min, self.args.delay_max),
                reload_probability=self.args.reload_prob,
                update_registration_prob=self.args.update_registration_prob,
                master_key=self.args.master_key,
                stats=self.stats,
                wait_for_approval=self.args.wait_for_approval,
                approval_timeout=self.args.approval_timeout,
            )
            self.clients.append(client)

        # Start auto-approver if needed
        approver_task = None
        if self.args.wait_for_approval and self.args.master_key:
            self.auto_approver = AutoApprover(self.args.url, self.args.master_key, self.stats)
            # For now, auto-approval is manual - admin needs to approve in real-time
            # A full implementation would use WebSocket to monitor new registrations

        # Run all clients concurrently
        print(f"Starting {self.args.clients} clients...\n")
        self.stats.clients_started = self.args.clients

        tasks = [client.run() for client in self.clients]

        if approver_task:
            tasks.append(approver_task)

        await asyncio.gather(*tasks, return_exceptions=True)

        # Cleanup
        if self.auto_approver:
            self.auto_approver.stop()

        self.stats.finalize()
        self.print_results()

    def print_results(self):
        """Print test results"""
        print(f"\n{'=' * 60}")
        print(f"Stress Test Results")
        print(f"{'=' * 60}\n")

        # Overall summary
        summary = self.stats.get_summary()
        print("Overall Statistics:")
        for key, value in summary.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")

        print(f"\nRequest Statistics:")
        print(f"{'-' * 60}")

        # Individual request stats
        for req_stats in [
            self.stats.register,
            self.stats.update_registration,
            self.stats.verify_user,
            self.stats.question_start,
            self.stats.submit_answer,
            self.stats.approve_user,
        ]:
            if req_stats.success_count > 0 or req_stats.failure_count > 0:
                stats = req_stats.get_stats()
                print(f"\n{stats['name']}:")
                for key, value in stats.items():
                    if key != "name":
                        print(f"  {key.replace('_', ' ').title()}: {value}")

                if req_stats.errors:
                    print(f"  Errors:")
                    for error, count in req_stats.errors.items():
                        print(f"    {error}: {count}")

        print(f"\n{'=' * 60}\n")


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Stress test WebQuiz server with concurrent users", formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "-u",
        "--url",
        type=str,
        default="http://localhost:8080",
        help="Server URL (default: http://localhost:8080)",
    )

    parser.add_argument(
        "-c",
        "--clients",
        type=int,
        default=10,
        help="Number of concurrent clients (default: 10)",
    )

    parser.add_argument(
        "--delay-min",
        type=float,
        default=0.5,
        help="Minimum delay between answers in seconds (default: 0.5)",
    )

    parser.add_argument(
        "--delay-max",
        type=float,
        default=2.0,
        help="Maximum delay between answers in seconds (default: 2.0)",
    )

    parser.add_argument(
        "--reload-prob",
        type=float,
        default=0.1,
        help="Probability of page reload between questions (0.0-1.0, default: 0.1)",
    )

    parser.add_argument(
        "--update-registration-prob",
        type=float,
        default=0.2,
        help="Probability of updating registration after registering (0.0-1.0, default: 0.2)",
    )

    parser.add_argument(
        "--wait-for-approval",
        action="store_true",
        help="Wait for admin approval before starting quiz",
    )

    parser.add_argument(
        "--no-wait-for-approval",
        action="store_true",
        help="Don't wait for approval (assume auto-approved)",
    )

    parser.add_argument(
        "--approval-timeout",
        type=float,
        default=30.0,
        help="Timeout for waiting for approval in seconds (default: 30.0)",
    )

    parser.add_argument(
        "-k",
        "--master-key",
        type=str,
        help="Master key for admin operations (enables auto-approval)",
    )

    return parser.parse_args()


async def async_main():
    """Async main entry point"""
    args = parse_args()

    # Validate arguments
    if args.delay_min < 0 or args.delay_max < 0:
        print("Error: Delay values must be non-negative")
        return 1

    if args.delay_min > args.delay_max:
        print("Error: delay-min must be less than or equal to delay-max")
        return 1

    if not (0.0 <= args.reload_prob <= 1.0):
        print("Error: reload-prob must be between 0.0 and 1.0")
        return 1

    if not (0.0 <= args.update_registration_prob <= 1.0):
        print("Error: update-registration-prob must be between 0.0 and 1.0")
        return 1

    if args.clients <= 0:
        print("Error: Number of clients must be positive")
        return 1

    # Determine approval mode
    if args.no_wait_for_approval:
        args.wait_for_approval = False
    # If not explicitly set, default based on whether master key is provided
    elif not hasattr(args, "wait_for_approval") or not args.wait_for_approval:
        args.wait_for_approval = False

    # Run test
    coordinator = StressTestCoordinator(args)
    try:
        await coordinator.run()
        return 0
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        coordinator.stats.finalize()
        coordinator.print_results()
        return 0


def main():
    """Main entry point for CLI"""
    try:
        return asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        return 0


if __name__ == "__main__":
    sys.exit(main())
