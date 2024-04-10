from aws_scrapper import AwsRegistrator


def test_steps(aws_instance: AwsRegistrator) -> None:
    """Test registration steps"""
    aws_instance.open_page()
    aws_instance.step_one()
    aws_instance.step_two()
    aws_instance.step_three()
    aws_instance.driver.quit()
