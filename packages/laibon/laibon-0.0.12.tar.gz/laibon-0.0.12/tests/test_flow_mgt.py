import unittest

from laibon import common, rtf, exception


class ErrorResult(common.ActivityResult):
    ERROR = "error"


def error():
    return ErrorResult.ERROR


class Activity1(common.Activity):
    KEY = common.ContainerKey("Activity1")

    def process(self, data_container: common.Container):
        res = data_container.get(self.KEY)
        data_container.put(self.KEY, "Visited")
        if res is None:
            return ErrorResult.ERROR
        return common.goto_next()


class Activity2(common.Activity):
    KEY = common.ContainerKey("Activity2")

    def process(self, data_container: common.Container):
        res = data_container.get(self.KEY)
        data_container.put(self.KEY, "Visited")
        if res is None:
            return error()
        return common.goto_next()


class Activity3(common.Activity):
    KEY = common.ContainerKey("Activity3")

    def process(self, data_container: common.Container):
        res = data_container.get(self.KEY)
        data_container.put(self.KEY, "Visited")
        if res is None:
            return error()
        return common.goto_next()


class Activity4(common.Activity):
    KEY = common.ContainerKey("Activity4")

    def process(self, data_container: common.Container):
        res = data_container.get(self.KEY)
        data_container.put(self.KEY, "Visited")
        if res is None:
            return error()
        return common.goto_next()


class TestFlowDefinitions(unittest.TestCase):

    def test_complete_flow(self):
        flow = rtf.FlowDefinition() \
            .add(Activity1).jump_default(Activity2) \
            .add(Activity2).jump_default(Activity3) \
            .add(Activity3).jump_default(Activity4) \
            .add(Activity4)

        data_container = common.Container()
        data_container.put(Activity1.KEY, "NotVisited")
        data_container.put(Activity2.KEY, "NotVisited")
        data_container.put(Activity3.KEY, "NotVisited")
        data_container.put(Activity4.KEY, "NotVisited")

        runner = rtf.FlowRunner(data_container)
        runner.run_flow(flow)
        self.assertEqual(data_container.get(Activity1.KEY), "Visited")
        self.assertEqual(data_container.get(Activity2.KEY), "Visited")
        self.assertEqual(data_container.get(Activity3.KEY), "Visited")
        self.assertEqual(data_container.get(Activity4.KEY), "Visited")

    def test_conditional_jumps_flow(self):
        flow = rtf.FlowDefinition() \
            .add(Activity1) \
            .jump_if(ErrorResult.ERROR, Activity3) \
            .jump_default(Activity2) \
            .add(Activity2).jump_default(Activity3) \
            .add(Activity3).jump_default(Activity4) \
            .add(Activity4)

        data_container = common.Container()
        data_container.put(Activity2.KEY, "NotVisited")
        data_container.put(Activity3.KEY, "NotVisited")
        data_container.put(Activity4.KEY, "NotVisited")

        runner = rtf.FlowRunner(data_container)
        runner.run_flow(flow)
        self.assertEqual(data_container.get(Activity1.KEY), "Visited")
        self.assertEqual(data_container.get(Activity2.KEY), "NotVisited")
        self.assertEqual(data_container.get(Activity3.KEY), "Visited")
        self.assertEqual(data_container.get(Activity4.KEY), "Visited")

    def test_missing_activity_in_flow(self):
        with self.assertRaises(exception.InvalidFlowDefinition) as context:
            flow = rtf.FlowDefinition() \
                .add(Activity1) \
                .jump_if(ErrorResult.ERROR, Activity3) \
                .jump_default(Activity2) \
                .add(Activity3).jump_default(Activity4) \
                .add(Activity4)

            data_container = common.Container()
            data_container.put(Activity1.KEY, "NotVisited")
            data_container.put(Activity2.KEY, "NotVisited")
            data_container.put(Activity3.KEY, "NotVisited")
            data_container.put(Activity4.KEY, "NotVisited")

            runner = rtf.FlowRunner(data_container)
            runner.run_flow(flow)
        self.assertEqual("Flow is not configured correctly. Activity2 is missing", context.exception.get_message())

    def test_against_backward_jumps_in_flow(self):
        with self.assertRaises(exception.InvalidFlowDefinition) as context:
            flow = rtf.FlowDefinition() \
                .add(Activity1).jump_default(Activity2) \
                .add(Activity2).jump_default(Activity1) \
                .add(Activity3).jump_default(Activity4) \
                .add(Activity4)

            data_container = common.Container()
            data_container.put(Activity1.KEY, "NotVisited")
            data_container.put(Activity2.KEY, "NotVisited")
            data_container.put(Activity3.KEY, "NotVisited")
            data_container.put(Activity4.KEY, "NotVisited")

            runner = rtf.FlowRunner(data_container)
            runner.run_flow(flow)
        self.assertEqual("Invalid jump location", context.exception.get_message())


if __name__ == '__main__':
    unittest.main()
